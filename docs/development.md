# Разработка

## Требования

- Python 3.14;
- uv;
- Git.

## Установка и запуск

```bash
uv sync --all-groups
uv run fastapi dev src/portable_agent/main.py
```

Swagger UI доступен по адресу `http://127.0.0.1:8000/docs`, health check —
`http://127.0.0.1:8000/health/live`.

## TDD

Работа идёт коротким циклом:

1. Red — тест описывает новое поведение и падает.
2. Green — минимальный код делает тест зелёным.
3. Refactor — код упрощается без изменения поведения.

Большинство тестов должны проверять `services` без FastAPI. HTTP-тесты проверяют только контракт,
валидацию и передачу вызова сервису.

## Проверки перед PR

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv run mkdocs build --strict
```
