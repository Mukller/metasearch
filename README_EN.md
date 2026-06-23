<div align="center">

[Русский](README.md) • **English**

</div>

# metasearch

Self-hosted search aggregator. Queries multiple search engines in parallel,
merges and deduplicates results. No JS trackers, no telemetry.

## Run

```bash
pip install metasearch
metasearch
# → http://localhost:8080

metasearch --port 9090 --host 0.0.0.0
```

## Features

- Aggregates DuckDuckGo, Brave Search, Bing
- Parallel requests (asyncio + httpx)
- URL deduplication
- Ranking by mention frequency
- Simple web interface
- JSON API (`/api/search?q=...`)

## API

```bash
curl "http://localhost:8080/api/search?q=python+asyncio&engines=ddg,brave"
```

```json
{
  "query": "python asyncio",
  "results": [
    { "title": "...", "url": "...", "snippet": "...", "score": 3, "sources": ["ddg", "brave"] }
  ],
  "total": 15,
  "took_ms": 420
}
```

## Config

```toml
# config.toml
port = 8080
timeout = 5.0
max_results_per_engine = 10
engines = ["ddg", "brave", "bing"]
```
