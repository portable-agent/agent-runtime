from portable_agent.models.proposal import ActionPlan, Risk, UserContext
from portable_agent.repositories.model_repository import ModelRepository
from portable_agent.repositories.policy_repository import PolicyRepository


class ProposalService:
    def __init__(self, model: ModelRepository, policy: PolicyRepository) -> None:
        self._model = model
        self._policy = policy

    async def propose(self, text: str, context: UserContext) -> ActionPlan | None:
        reply = await self._model.propose(text, context)
        if reply is None:
            return None
        if reply.connector not in context.available_tools:
            return None

        risk = await self._policy.get_risk(reply, context)
        return ActionPlan(
            kind=reply.kind,
            connector=reply.connector,
            payload=reply.payload,
            explanation=reply.explanation,
            risk=risk,
            requires_approval=risk is not Risk.LOW,
        )
