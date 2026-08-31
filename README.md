# Agent Runtime

`agent-runtime` — stateless Python-сервис платформы Portable Agent. Он получает текст пользователя,
контекст и список доступных коннекторов, затем готовит типизированное предложение действия.

Сервис **не исполняет действия**, не хранит деньги, токены и историю. Исполнение, подтверждение
пользователем и аудит принадлежат `action-service`.

## Что уже есть

- HTTP API на FastAPI;
- простой MVC-подобный каркас;
- локальные demo-адаптеры модели и policy для разработки без внешних сервисов;
- результат с `proposal` или `clarification` для первого действия `calendar.create_event`;
- Ruff, strict mypy, pytest и проверка покрытия;
- русская документация MkDocs/Backstage TechDocs.

## Структура

```text
src/portable_agent/
├── controllers/   # HTTP-вход
├── services/      # сценарии приложения
├── repositories/  # клиенты внешней AI-модели и policy
├── models/        # внутренние модели
├── schemas/       # HTTP request/response
├── config/        # сборка зависимостей
├── exceptions/    # ошибки приложения
└── main.py        # создание FastAPI
```

## Быстрый старт

```bash
uv sync --all-groups
uv run fastapi dev src/portable_agent/main.py
```

Проверки:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv run mkdocs build --strict
```

Подробности: [docs/index.md](docs/index.md). Правила для разработчиков и AI-агентов:
[AGENTS.md](AGENTS.md).

## Первый сценарий

Сервис принимает только `calendar.create_event`. Для готового предложения нужны `title`, `startAt`,
`endAt` и `timeZone`; исполнитель первой версии называется `fake-calendar`. Если полей не хватает,
ответ содержит `clarification`, а `proposal` остаётся `null`. Готовое предложение всегда содержит
`requires_approval: true`.

Локальная demo-модель не понимает свободную речь. Для полного сквозного теста используй точный
формат:

```text
Создай встречу "Обсуждение проекта" с 2026-09-01T12:00:00+03:00 до 2026-09-01T12:30:00+03:00
```

Настоящий разбор обычной речи появится в отдельном адаптере AI-модели.
