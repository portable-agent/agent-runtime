import re
from typing import Protocol

from portable_agent.models.proposal import ModelReply, UserContext


class IntentModel(Protocol):
    """Внешняя модель, которая превращает текст в типизированный ответ."""

    async def propose(self, text: str, context: UserContext) -> ModelReply | None: ...


class DemoIntentModel:
    """Локальная заглушка для разработки без внешней AI-модели."""

    async def propose(self, text: str, context: UserContext) -> ModelReply | None:
        normalized_text = text.casefold()
        if "встреч" not in normalized_text and "календар" not in normalized_text:
            return None

        connector = next(
            (
                name
                for name in ("google-calendar", "fake-calendar")
                if name in context.available_tools
            ),
            None,
        )
        if connector is None:
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
            connector=connector,
            payload=payload,
            explanation="Создать событие календаря по команде пользователя",
        )
