from portable_agent.domain.models import ConversationContext, ProposedToolCall


class DeterministicDevelopmentModel:
    """Safe local adapter; production providers implement the same port."""

    async def propose(
        self, utterance: str, context: ConversationContext
    ) -> ProposedToolCall | None:
        normalized = utterance.casefold()
        if "встреч" not in normalized and "календар" not in normalized:
            return None
        return ProposedToolCall(
            kind="calendar.create_event",
            connector="google-calendar",
            payload={"source_text": utterance, "timezone": context.timezone},
            explanation="Создать событие календаря по команде пользователя",
        )
