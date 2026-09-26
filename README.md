# Agent Runtime

`agent-runtime` — stateless Python-сервис платформы Portable Agent. Он получает текст пользователя,
контекст и список доступных коннекторов, затем готовит типизированное предложение действия.

Сервис **не исполняет действия**, не хранит деньги, токены и историю. Исполнение, подтверждение
пользователем и аудит принадлежат `action-service`.

## Что уже есть

- HTTP API на FastAPI;
- Bearer JWT с проверкой подписи, issuer, audience и срока жизни;
- контракт `portable-agent/contracts` версии `2.1.0`;
- простой MVC-подобный каркас;
- внешний порт `IntentModel` и локальная `DemoIntentModel` для разработки без AI-сервиса;
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

Для `POST /api/v1/proposals` нужен Bearer token с audience `agent-runtime`. Идентификаторы tenant и
пользователя сервис берёт из claims `tenant_id` и `sub`; передать или подменить их в JSON нельзя.

Основные переменные окружения:

- `AGENT_OIDC_ISSUER_URL` — issuer токена;
- `AGENT_OIDC_JWKS_URL` — публичные ключи OIDC;
- `AGENT_OIDC_AUDIENCE` — ожидаемый audience, по умолчанию `agent-runtime`;
- `AGENT_ALLOWED_HOSTS` — JSON-массив разрешённых Host;
- `AGENT_DOCS_ENABLED` — включает Swagger только там, где он нужен.
- `AGENT_MODEL_PROVIDER` — `demo` или `openai-compatible`;
- `AGENT_MODEL_BASE_URL` — адрес OpenAI-совместимого API;
- `AGENT_MODEL_NAME` — имя модели у выбранного провайдера;
- `AGENT_MODEL_API_KEY` — необязательный ключ; локальной Ollama он не нужен;
- `AGENT_MODEL_TIMEOUT_SECONDS` — тайм-аут ответа модели, по умолчанию 30 секунд.

По умолчанию включена детерминированная `demo`-модель. Для локальной Ollama:

```env
AGENT_MODEL_PROVIDER=openai-compatible
AGENT_MODEL_BASE_URL=http://localhost:11434/v1
AGENT_MODEL_NAME=qwen2.5:7b
```

Из контейнера вместо `localhost` используй адрес Ollama, заданный в deploy-конфигурации. Тот же
адаптер можно направить в NVIDIA NIM или другой совместимый API, поменяв URL, имя модели и ключ.
Облачный режим отправляет текст пользователя внешнему провайдеру и должен включаться явно.

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
`requiresApproval: true`.

Внешний запрос использует поля `text`, `timeZone` и `availableConnectors`. Проверенная копия схемы
лежит в `contracts/agent-runtime-api.yaml`; безопасное обновление выполняет
`scripts/update-contract.ps1`.

Локальная demo-модель не понимает свободную речь. Для детерминированного сквозного теста используй
точный формат:

```text
Создай встречу "Обсуждение проекта" с 2026-09-01T12:00:00+03:00 до 2026-09-01T12:30:00+03:00
```

`openai-compatible`-модель принимает обычные фразы, например:

```text
Поставь завтра в 19:00 созвон с Колей на полчаса
```

Ответ модели не исполняется напрямую: `ProposalService` проверяет вид действия, доступный коннектор
и типизированный payload. Исходный текст, ключ модели и полный ответ модели нельзя писать в логи.
