from portable_agent.application.ports import ModelGateway, PolicyGateway
from portable_agent.domain.models import ActionProposal, ConversationContext, RiskLevel


class ProposalService:
    def __init__(self, model: ModelGateway, policy: PolicyGateway) -> None:
        self._model = model
        self._policy = policy

    async def propose(self, utterance: str, context: ConversationContext) -> ActionProposal | None:
        tool_call = await self._model.propose(utterance, context)
        if tool_call is None:
            return None
        if tool_call.connector not in context.available_connectors:
            return None

        risk = await self._policy.classify(tool_call, context)
        return ActionProposal(
            kind=tool_call.kind,
            connector=tool_call.connector,
            payload=tool_call.payload,
            explanation=tool_call.explanation,
            risk=risk,
            requires_approval=risk is not RiskLevel.LOW,
        )
