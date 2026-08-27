from typing import Protocol

from portable_agent.domain.models import ConversationContext, ProposedToolCall, RiskLevel


class ModelGateway(Protocol):
    async def propose(
        self, utterance: str, context: ConversationContext
    ) -> ProposedToolCall | None: ...


class PolicyGateway(Protocol):
    async def classify(self, call: ProposedToolCall, context: ConversationContext) -> RiskLevel: ...
