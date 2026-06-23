"""Агрегация и дедупликация результатов."""

import asyncio
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import httpx

from .engines import Result, ENGINES


@dataclass
class AggResult:
    title: str
    url: str
    snippet: str
    score: int          # сколько движков нашли эту ссылку
    sources: list[str]


@dataclass
class SearchResponse:
    query: str
    results: list[AggResult]
    total: int
    took_ms: int
    errors: list[str] = field(default_factory=list)


def _normalize_url(url: str) -> str:
    """Убираем trailing slash и fragment для сравнения."""
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/").lower()


async def aggregate(
    query: str,
    engine_names: list[str],
    n: int = 10,
    timeout: float = 7.0,
) -> SearchResponse:
    t0 = time.monotonic()
    errors: list[str] = []

    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    async with httpx.AsyncClient(limits=limits, follow_redirects=True) as client:
        tasks = {}
        for name in engine_names:
            fn = ENGINES.get(name)
            if fn:
                tasks[name] = asyncio.create_task(fn(query, client, n))

        done = await asyncio.gather(*tasks.values(), return_exceptions=True)

    all_results: list[Result] = []
    for name, res in zip(tasks.keys(), done):
        if isinstance(res, Exception):
            errors.append(f"{name}: {res}")
        else:
            all_results.extend(res)

    # дедупликация по нормализованному URL
    seen: dict[str, AggResult] = {}
    for r in all_results:
        key = _normalize_url(r.url)
        if key in seen:
            seen[key].score += 1
            if r.source not in seen[key].sources:
                seen[key].sources.append(r.source)
        else:
            seen[key] = AggResult(
                title=r.title,
                url=r.url,
                snippet=r.snippet,
                score=1,
                sources=[r.source],
            )

    results = sorted(seen.values(), key=lambda x: -x.score)
    took_ms = int((time.monotonic() - t0) * 1000)

    return SearchResponse(
        query=query,
        results=results,
        total=len(results),
        took_ms=took_ms,
        errors=errors,
    )
