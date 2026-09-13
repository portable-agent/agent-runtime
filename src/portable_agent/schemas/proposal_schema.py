from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from portable_agent.models.proposal import ActionPlan, Clarification, UserContext
from portable_agent.models.user import TokenUser


class ContextData(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    locale: str = Field(default="ru-RU", min_length=2, max_length=16)
    time_zone: str = Field(
        default="Europe/Moscow",
        alias="timeZone",
        min_length=1,
        max_length=100,
        pattern=r"^(UTC|[A-Za-z_]+(?:/[A-Za-z0-9_+-]+)+)$",
    )
    available_connectors: set[Literal["fake-calendar"]] = Field(
        default_factory=set,
        alias="availableConnectors",
    )

    def to_model(self, user: TokenUser) -> UserContext:
        return UserContext(
            tenant_id=user.tenant_id,
            user_id=user.user_id,
            locale=self.locale,
            timezone=self.time_zone,
            available_tools=self.available_connectors,
        )


class ProposalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=10_000)
    context: ContextData


class ProposalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal: ActionPlan | None
    clarification: Clarification | None
