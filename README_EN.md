# metasearch

Self-hosted search aggregator. Queries multiple engines in parallel, merges and deduplicates results. No JS trackers, no telemetry.

## Usage

```bash
pip install metasearch
metasearch  # http://localhost:8080

curl "http://localhost:8080/api/search?q=python"
```
