# Agent Runtime

Stateless AI-runtime платформы Portable Agent. Он превращает пользовательский текст и контекст
в типизированные предложения действий, но не исполняет их сам. Исполнение, approval и аудит принадлежат
`action-service`, поэтому смена LLM-провайдера не меняет trust boundary.

## Стек

Python 3.14, FastAPI, Pydantic 2, uv, Ruff, mypy и pytest.

## Локальный запуск

```bash
uv sync --all-groups
uv run fastapi dev src/portable_agent/main.py
```

В development-профиле используется детерминированный gateway без внешней модели. Следующий адаптер
реализует тот же `ModelGateway` для выбранного LLM и получает ключ только через secret manager.
