from uuid import uuid4

import pytest

from portable_agent.models.proposal import UserContext
from portable_agent.repositories.model_repository import DemoIntentModel


def context(*connectors: str) -> UserContext:
    return UserContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        timezone="Europe/Moscow",
        available_tools=set(connectors or ("fake-calendar",)),
    )


@pytest.mark.asyncio
async def test_demo_model_when_command_is_complete_should_return_calendar_reply() -> None:
    model = DemoIntentModel()

    reply = await model.propose(
        'Создай встречу "Обсуждение проекта" с 2026-09-01T12:00:00+03:00 '
        "до 2026-09-01T12:30:00+03:00",
        context(),
    )

    assert reply is not None
    assert reply.kind == "calendar.create_event"
    assert reply.connector == "fake-calendar"
    assert reply.payload == {
        "title": "Обсуждение проекта",
        "startAt": "2026-09-01T12:00:00+03:00",
        "endAt": "2026-09-01T12:30:00+03:00",
        "timeZone": "Europe/Moscow",
    }


@pytest.mark.asyncio
async def test_demo_model_when_google_calendar_is_available_should_choose_it() -> None:
    model = DemoIntentModel()

    reply = await model.propose(
        'Создай встречу "Обсуждение проекта" с 2026-09-01T12:00:00+03:00 '
        "до 2026-09-01T12:30:00+03:00",
        context("fake-calendar", "google-calendar"),
    )

    assert reply is not None
    assert reply.connector == "google-calendar"


@pytest.mark.asyncio
async def test_demo_model_when_text_is_not_calendar_command_should_return_none() -> None:
    model = DemoIntentModel()

    reply = await model.propose("Привет", context())

    assert reply is None


@pytest.mark.asyncio
async def test_demo_model_when_calendar_connector_is_unavailable_should_return_none() -> None:
    model = DemoIntentModel()

    reply = await model.propose(
        'Создай встречу "Обсуждение проекта" с 2026-09-01T12:00:00+03:00 '
        "до 2026-09-01T12:30:00+03:00",
        context("wallet"),
    )

    assert reply is None
