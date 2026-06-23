# metasearch

Self-hosted поисковый агрегатор. Запрашивает несколько поисковиков параллельно, объединяет и дедуплицирует результаты. Минимум зависимостей, никаких JS-трекеров, никакой телеметрии.

## Что умеет

- Агрегирует DuckDuckGo, Brave Search, Bing
- Параллельные запросы (asyncio + httpx)
- Дедупликация по URL
- Ранжирование по частоте упоминания
- Простой веб-интерфейс
- JSON API (`/api/search?q=...`)

## Установка

```bash
pip install metasearch
# или
git clone ...
pip install -e .
```

## Запуск

```bash
metasearch
# Сервер на http://localhost:8080

metasearch --port 9090 --host 0.0.0.0
```

## API

```bash
# Поиск через JSON API
curl "http://localhost:8080/api/search?q=python+asyncio&engines=ddg,brave"

# Ответ:
{
  "query": "python asyncio",
  "results": [
    {
      "title": "...",
      "url": "...",
      "snippet": "...",
      "score": 3,
      "sources": ["ddg", "brave"]
    }
  ],
  "total": 15,
  "took_ms": 420
}
```

## Настройка

```toml
# config.toml
port = 8080
timeout = 5.0
max_results_per_engine = 10
engines = ["ddg", "brave", "bing"]
```
