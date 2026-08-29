from uuid import uuid4

import pytest

from portable_agent.models.proposal import ModelReply, Risk, UserContext
from portable_agent.services.proposal_service import ProposalService


class FakeModel:
    def __init__(self, result: ModelReply | None) -> None:
        self.result = result

    async def propose(self, text: str, context: UserContext) -> ModelReply | None:
        del text, context
        return self.result


class FakePolicy:
    def __init__(self, risk: Risk) -> None:
        self.risk = risk

    async def get_risk(self, reply: ModelReply, context: UserContext) -> Risk:
        del reply, context
        return self.risk


def context(*tools: str) -> UserContext:
    return UserContext(tenant_id=uuid4(), user_id=uuid4(), available_tools=set(tools))


@pytest.mark.asyncio
async def test_propose_when_connector_available_returns_typed_proposal() -> None:
    call = ModelReply(
        kind="calendar.create_event",
        connector="google-calendar",
        payload={"title": "Demo"},
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.MEDIUM))

    proposal = await service.propose("Создай встречу", context("google-calendar"))

    assert proposal is not None
    assert proposal.kind == "calendar.create_event"
    assert proposal.requires_approval is True


@pytest.mark.asyncio
async def test_propose_when_model_returns_no_call_returns_none() -> None:
    service = ProposalService(FakeModel(None), FakePolicy(Risk.LOW))

    assert await service.propose("Привет", context("google-calendar")) is None


@pytest.mark.asyncio
async def test_propose_when_connector_unavailable_rejects_proposal() -> None:
    call = ModelReply(
        kind="wallet.transfer",
        connector="wallet",
        payload={"amount": "10"},
        explanation="Transfer funds",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.HIGH))

    assert await service.propose("Переведи деньги", context("google-calendar")) is None


@pytest.mark.asyncio
async def test_propose_when_risk_is_low_does_not_require_approval() -> None:
    call = ModelReply(
        kind="calendar.read",
        connector="google-calendar",
        payload={},
        explanation="Read calendar",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.LOW))

    proposal = await service.propose("Что в календаре", context("google-calendar"))

    assert proposal is not None
    assert proposal.requires_approval is False
