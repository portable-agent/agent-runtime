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
async def test_propose_full_calendar_event_returns_approval_proposal() -> None:
    call = ModelReply(
        kind="calendar.create_event",
        connector="fake-calendar",
        payload={
            "title": "Обсуждение проекта",
            "startAt": "2026-09-01T12:00:00+03:00",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
        },
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.LOW))

    result = await service.propose("Создай встречу", context("fake-calendar"))

    assert result.proposal is not None
    assert result.proposal.kind == "calendar.create_event"
    assert result.proposal.payload == call.payload
    assert result.proposal.risk is Risk.LOW
    assert result.proposal.requires_approval is True
    assert result.clarification is None


@pytest.mark.asyncio
async def test_propose_incomplete_calendar_event_returns_clarification() -> None:
    call = ModelReply(
        kind="calendar.create_event",
        connector="fake-calendar",
        payload={"title": "Обсуждение проекта"},
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.MEDIUM))

    result = await service.propose("Создай встречу", context("fake-calendar"))

    assert result.proposal is None
    assert result.clarification is not None
    assert result.clarification.missing_fields == ["startAt", "endAt", "timeZone"]
    assert result.clarification.question == (
        "Укажи время начала, время окончания и часовой пояс встречи."
    )


@pytest.mark.asyncio
async def test_propose_when_model_returns_no_call_returns_none() -> None:
    service = ProposalService(FakeModel(None), FakePolicy(Risk.LOW))

    result = await service.propose("Привет", context("fake-calendar"))

    assert result.proposal is None
    assert result.clarification is None


@pytest.mark.asyncio
async def test_propose_when_connector_unavailable_rejects_proposal() -> None:
    call = ModelReply(
        kind="calendar.create_event",
        connector="fake-calendar",
        payload={
            "title": "Demo",
            "startAt": "2026-09-01T12:00:00+03:00",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
        },
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.HIGH))

    result = await service.propose("Создай встречу", context("google-calendar"))

    assert result.proposal is None
    assert result.clarification is None


@pytest.mark.asyncio
async def test_propose_when_action_is_not_allowed_returns_empty_result() -> None:
    call = ModelReply(
        kind="wallet.transfer",
        connector="wallet",
        payload={"amount": "10"},
        explanation="Transfer funds",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.HIGH))

    result = await service.propose("Переведи деньги", context("wallet"))

    assert result.proposal is None
    assert result.clarification is None


@pytest.mark.asyncio
async def test_propose_when_only_title_is_missing_asks_for_title() -> None:
    call = ModelReply(
        kind="calendar.create_event",
        connector="fake-calendar",
        payload={
            "startAt": "2026-09-01T12:00:00+03:00",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
        },
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.MEDIUM))

    result = await service.propose("Создай встречу", context("fake-calendar"))

    assert result.clarification is not None
    assert result.clarification.question == "Укажи название встречи."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "title": "   ",
            "startAt": "2026-09-01T12:00:00+03:00",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
        },
        {
            "title": "Demo",
            "startAt": "not-a-date",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
        },
        {
            "title": "Demo",
            "startAt": 0,
            "endAt": 1800,
            "timeZone": "Europe/Moscow",
        },
        {
            "title": "Demo",
            "startAt": "2026-09-01T13:00:00+03:00",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
        },
        {
            "title": "Demo",
            "startAt": "2026-09-01T12:00:00+03:00",
            "endAt": "2026-09-01T12:30:00+03:00",
            "timeZone": "Europe/Moscow",
            "hidden": "value",
        },
    ],
)
async def test_propose_when_calendar_payload_is_invalid_returns_empty_result(
    payload: dict[str, object],
) -> None:
    call = ModelReply(
        kind="calendar.create_event",
        connector="fake-calendar",
        payload=payload,
        explanation="Create event",
    )
    service = ProposalService(FakeModel(call), FakePolicy(Risk.MEDIUM))

    result = await service.propose("Создай встречу", context("fake-calendar"))

    assert result.proposal is None
    assert result.clarification is None
