# Архитектура

## Поток запроса

```mermaid
sequenceDiagram
    participant Client as Клиент
    participant Controller as Controller
    participant Service as ProposalService
    participant Model as ModelRepository
    participant Policy as PolicyRepository

    Client->>Controller: POST /api/v1/proposals
    Controller->>Service: propose(text, context)
    Service->>Model: propose(text, context)
    Model-->>Service: ModelReply или null
    alt Не хватает обязательных полей
        Service-->>Controller: Clarification
    else Полный calendar.create_event
        Service->>Policy: get_risk(reply, context)
        Policy-->>Service: Risk
        Service-->>Controller: ActionPlan
    end
    Controller-->>Client: ProposalResponse
```

## Зависимости папок

```text
controllers -> services -> repositories
      |            |
      v            v
   schemas       models

config собирает реализации; main подключает controllers.
```

Зависимости направлены от HTTP к внутренней модели. `models` не импортирует FastAPI. Сервис не
хранит состояние между запросами.

`ProposalService` разрешает только `calendar.create_event`, проверяет поля `title`, `startAt`,
`endAt` и `timeZone`, а затем формирует предложение с обязательным подтверждением. Проверка не
зависит от demo-модели, поэтому будущий AI-адаптер не меняет продуктовые правила.

Внутренняя модель `CalendarEvent` запрещает лишние поля, проверяет даты, часовой пояс, размеры строк,
уникальность участников и правило `endAt > startAt`. В `ActionPlan` попадает нормализованный payload
с внешними именами полей из репозитория `contracts`.

Ответ имеет две необязательные части:

- `proposal` — готовые точные аргументы для передачи в `action-service`;
- `clarification` — вопрос и список полей, которые нужно получить от пользователя.

Одновременно заполнена только одна часть.

## Внешние контракты

HTTP-путь и старые имена полей (`utterance`, `actor_id`, `available_connectors`) сохранены для
совместимости с репозиторием `contracts`. Внутри используются более простые имена `text`, `user_id`
и `available_tools`; преобразование находится в HTTP-схеме.
