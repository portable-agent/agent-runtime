from typing import Protocol

from portable_agent.models.proposal import ModelReply, Risk, UserContext


class PolicyRepository(Protocol):
    async def get_risk(self, reply: ModelReply, context: UserContext) -> Risk: ...


class DemoPolicyRepository:
    """Фиксированный ответ для локального запуска, не продуктовая policy-модель."""

    async def get_risk(self, reply: ModelReply, context: UserContext) -> Risk:
        del reply, context
        return Risk.MEDIUM
