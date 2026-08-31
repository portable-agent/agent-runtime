from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Risk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ModelReply(BaseModel):
    kind: str = Field(min_length=1, max_length=80)
    connector: str = Field(min_length=1, max_length=80)
    payload: dict[str, Any]
    explanation: str = Field(min_length=1, max_length=500)


Email = Annotated[
    str,
    Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
]


class CalendarEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    start_at: datetime = Field(alias="startAt")
    end_at: datetime = Field(alias="endAt")
    time_zone: str = Field(
        alias="timeZone",
        max_length=100,
        pattern=r"^(UTC|[A-Za-z_]+(?:/[A-Za-z0-9_+-]+)+)$",
    )
    description: str | None = Field(default=None, max_length=2000)
    attendees: list[Email] = Field(default_factory=list, max_length=50)

    @field_validator("start_at", "end_at", mode="before")
    @classmethod
    def check_date_type(cls, value: object) -> object:
        if not isinstance(value, str):
            raise ValueError("date-time value must be a string")
        return value

    @model_validator(mode="after")
    def check_time(self) -> Self:
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise ValueError("startAt and endAt must include an offset")
        if self.end_at <= self.start_at:
            raise ValueError("endAt must be after startAt")
        if len(self.attendees) != len(set(self.attendees)):
            raise ValueError("attendees must be unique")
        return self


class ActionPlan(BaseModel):
    proposal_id: UUID = Field(default_factory=uuid4)
    kind: str
    connector: str
    payload: dict[str, Any]
    explanation: str
    risk: Risk
    requires_approval: bool


class Clarification(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    missing_fields: list[str]


class ProposalResult(BaseModel):
    proposal: ActionPlan | None = None
    clarification: Clarification | None = None


class UserContext(BaseModel):
    tenant_id: UUID
    user_id: UUID
    locale: str = Field(default="ru-RU", min_length=2, max_length=16)
    timezone: str = Field(default="Europe/Moscow", min_length=1, max_length=64)
    available_tools: set[str] = Field(default_factory=set)
