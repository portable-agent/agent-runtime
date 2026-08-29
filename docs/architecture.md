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
    Service->>Policy: get_risk(reply, context)
    Policy-->>Service: Risk
    Service-->>Controller: ActionPlan
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

## Внешние контракты

HTTP-путь и старые имена полей (`utterance`, `actor_id`, `available_connectors`) сохранены для
совместимости с репозиторием `contracts`. Внутри используются более простые имена `text`, `user_id`
и `available_tools`; преобразование находится в HTTP-схеме.
