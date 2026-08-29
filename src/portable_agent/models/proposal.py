from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Risk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ModelReply(BaseModel):
    kind: str = Field(min_length=1, max_length=80)
    connector: str = Field(min_length=1, max_length=80)
    payload: dict[str, Any]
    explanation: str = Field(min_length=1, max_length=500)


class ActionPlan(BaseModel):
    proposal_id: UUID = Field(default_factory=uuid4)
    kind: str
    connector: str
    payload: dict[str, Any]
    explanation: str
    risk: Risk
    requires_approval: bool


class UserContext(BaseModel):
    tenant_id: UUID
    user_id: UUID
    locale: str = Field(default="ru-RU", min_length=2, max_length=16)
    timezone: str = Field(default="Europe/Moscow", min_length=1, max_length=64)
    available_tools: set[str] = Field(default_factory=set)
