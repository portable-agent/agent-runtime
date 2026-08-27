from uuid import uuid4

import pytest

from portable_agent.application.proposal_service import ProposalService
from portable_agent.domain.models import (
    ConversationContext,
    ProposedToolCall,
    RiskLevel,
)


class FakeModel:
    def __init__(self, result: ProposedToolCall | None) -> None:
        self.result = result

    async def propose(
        self, utterance: str, context: ConversationContext
    ) -> ProposedToolCall | None:
        del utterance, context
        return self.result


class FakePolicy:
    def __init__(self, risk: RiskLevel) -> None:
        self.risk = risk

    async def classify(self, call: ProposedToolCall, context: ConversationContext) -> RiskLevel:
        del call, context
        return self.risk


def context(*connectors: str) -> ConversationContext:
    return ConversationContext(
        tenant_id=uuid4(), actor_id=uuid4(), available_connectors=set(connectors)
    )


@pytest.mark.asyncio
async def test_propose_when_connector_available_returns_typed_proposal() -> None:
    call = ProposedToolCall(
        kind="calendar.create_event",
        connector="google-calendar",
        payload={"title": "Demo"},
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(RiskLevel.MEDIUM))

    proposal = await service.propose("Создай встречу", context("google-calendar"))

    assert proposal is not None
    assert proposal.kind == "calendar.create_event"
    assert proposal.requires_approval is True


@pytest.mark.asyncio
async def test_propose_when_model_returns_no_call_returns_none() -> None:
    service = ProposalService(FakeModel(None), FakePolicy(RiskLevel.LOW))

    assert await service.propose("Привет", context("google-calendar")) is None


@pytest.mark.asyncio
async def test_propose_when_connector_unavailable_rejects_proposal() -> None:
    call = ProposedToolCall(
        kind="wallet.transfer",
        connector="wallet",
        payload={"amount": "10"},
        explanation="Transfer funds",
    )
    service = ProposalService(FakeModel(call), FakePolicy(RiskLevel.HIGH))

    assert await service.propose("Переведи деньги", context("google-calendar")) is None


@pytest.mark.asyncio
async def test_propose_when_risk_is_low_does_not_require_approval() -> None:
    call = ProposedToolCall(
        kind="calendar.read",
        connector="google-calendar",
        payload={},
        explanation="Read calendar",
    )
    service = ProposalService(FakeModel(call), FakePolicy(RiskLevel.LOW))

    proposal = await service.propose("Что в календаре", context("google-calendar"))

    assert proposal is not None
    assert proposal.requires_approval is False
