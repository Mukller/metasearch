"""Адаптеры поисковых движков."""

import re
import urllib.parse
from dataclasses import dataclass

import httpx


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


@dataclass
class Result:
    title: str
    url: str
    snippet: str
    source: str


async def search_ddg(query: str, client: httpx.AsyncClient, n: int = 10) -> list[Result]:
    """DuckDuckGo HTML-поиск (без API-ключа)."""
    params = {"q": query, "kl": "ru-ru", "kp": "-2", "kn": "1"}
    try:
        r = await client.get(
            "https://html.duckduckgo.com/html/",
            params=params,
            headers={**HEADERS, "Accept": "text/html"},
            follow_redirects=True,
            timeout=6,
        )
        r.raise_for_status()
    except Exception:
        return []

    results = []
    # Парсим HTML вручную — без lxml/bs4
    blocks = re.findall(
        r'<a class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'<a class="result__snippet"[^>]*>(.*?)</a>',
        r.text,
        re.DOTALL,
    )
    for url, title, snippet in blocks[:n]:
        url = _clean_ddg_url(url)
        title = _strip_tags(title)
        snippet = _strip_tags(snippet)
        if url and title:
            results.append(Result(title=title, url=url, snippet=snippet, source="ddg"))
    return results


def _clean_ddg_url(url: str) -> str:
    # DDG оборачивает ссылки в редирект
    if "duckduckgo.com/l/" in url:
        m = re.search(r"uddg=([^&]+)", url)
        if m:
            return urllib.parse.unquote(m.group(1))
    return url


async def search_brave(query: str, client: httpx.AsyncClient, n: int = 10) -> list[Result]:
    """Brave Search (без API-ключа, через HTML)."""
    params = {"q": query, "source": "web", "count": str(n)}
    try:
        r = await client.get(
            "https://search.brave.com/search",
            params=params,
            headers={**HEADERS, "Accept": "text/html"},
            follow_redirects=True,
            timeout=6,
        )
        r.raise_for_status()
    except Exception:
        return []

    results = []
    # Ищем блоки с результатами
    blocks = re.findall(
        r'<a[^>]+class="[^"]*result-header[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?<p[^>]*class="[^"]*snippet[^"]*"[^>]*>(.*?)</p>',
        r.text,
        re.DOTALL,
    )
    for url, title, snippet in blocks[:n]:
        title = _strip_tags(title)
        snippet = _strip_tags(snippet)
        if url.startswith("http") and title:
            results.append(Result(title=title, url=url, snippet=snippet, source="brave"))
    return results


async def search_bing(query: str, client: httpx.AsyncClient, n: int = 10) -> list[Result]:
    """Bing через HTML."""
    params = {"q": query, "count": str(n), "setlang": "ru"}
    try:
        r = await client.get(
            "https://www.bing.com/search",
            params=params,
            headers={**HEADERS, "Accept": "text/html"},
            follow_redirects=True,
            timeout=6,
        )
        r.raise_for_status()
    except Exception:
        return []

    results = []
    blocks = re.findall(
        r'<h2[^>]*><a[^>]+href="([^"]+)"[^>]*>(.*?)</a></h2>'
        r'.*?<p[^>]*>(.*?)</p>',
        r.text,
        re.DOTALL,
    )
    for url, title, snippet in blocks[:n]:
        if not url.startswith("http"):
            continue
        title = _strip_tags(title)
        snippet = _strip_tags(snippet)
        if title:
            results.append(Result(title=title, url=url, snippet=snippet, source="bing"))
    return results


def _strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    s = re.sub(r"&quot;", '"', s)
    s = re.sub(r"&#39;", "'", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


ENGINES = {
    "ddg": search_ddg,
    "brave": search_brave,
    "bing": search_bing,
}
