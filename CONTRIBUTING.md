# Contributing

## Как помочь

Принимаю PR с:
- Новыми поисковыми движками
- Улучшением дедупликации
- Кешированием результатов
- Улучшением UI

## Как добавить движок

```python
class MyEngine(BaseEngine):
    name = "myengine"
    async def search(self, query: str, limit: int) -> list[Result]: ...
```

## Стиль

- `ruff format` и `ruff check`
- Движки независимы — без общего состояния
