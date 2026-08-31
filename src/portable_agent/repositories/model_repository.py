import re
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

        match = re.fullmatch(
            # The Russian demo command intentionally uses a Cyrillic preposition.
            r'Создай встречу "(?P<title>[^"]+)" с (?P<start>\S+) до (?P<end>\S+)',  # noqa: RUF001
            text,
            flags=re.IGNORECASE,
        )
        payload = (
            {
                "title": match.group("title"),
                "startAt": match.group("start"),
                "endAt": match.group("end"),
                "timeZone": context.timezone,
            }
            if match
            else {"source_text": text, "timeZone": context.timezone}
        )

        return ModelReply(
            kind="calendar.create_event",
            connector="fake-calendar",
            payload=payload,
            explanation="Создать событие календаря по команде пользователя",
        )
