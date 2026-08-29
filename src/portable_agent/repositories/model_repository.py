from typing import Protocol

from portable_agent.models.proposal import ModelReply, UserContext


class ModelRepository(Protocol):
    async def propose(self, text: str, context: UserContext) -> ModelReply | None: ...


class DemoModelRepository:
    """Локальная заглушка для разработки без внешней AI-модели."""

    async def propose(self, text: str, context: UserContext) -> ModelReply | None:
        normalized_text = text.casefold()
        if "встреч" not in normalized_text and "календар" not in normalized_text:
            return None

        return ModelReply(
            kind="calendar.create_event",
            connector="google-calendar",
            payload={"source_text": text, "timezone": context.timezone},
            explanation="Создать событие календаря по команде пользователя",
        )
