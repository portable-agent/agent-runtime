from uuid import UUID

from pydantic import BaseModel, Field

from portable_agent.models.proposal import ActionPlan, UserContext


class ContextData(BaseModel):
    tenant_id: UUID
    actor_id: UUID
    locale: str = Field(default="ru-RU", min_length=2, max_length=16)
    timezone: str = Field(default="Europe/Moscow", min_length=1, max_length=64)
    available_connectors: set[str] = Field(default_factory=set)

    def to_model(self) -> UserContext:
        return UserContext(
            tenant_id=self.tenant_id,
            user_id=self.actor_id,
            locale=self.locale,
            timezone=self.timezone,
            available_tools=self.available_connectors,
        )


class ProposalRequest(BaseModel):
    utterance: str = Field(min_length=1, max_length=10_000)
    context: ContextData


class ProposalResponse(BaseModel):
    proposal: ActionPlan | None
