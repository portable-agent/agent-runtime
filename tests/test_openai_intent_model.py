import json
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest

from portable_agent.models.proposal import UserContext
from portable_agent.repositories.openai_intent_model import OpenAIIntentModel


def context() -> UserContext:
    return UserContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        locale="ru-RU",
        timezone="Europe/Moscow",
        available_tools={"fake-calendar"},
    )


@pytest.mark.asyncio
async def test_openai_model_when_reply_has_action_should_return_model_reply() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url == "http://model.test/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert body["model"] == "qwen2.5:7b"
        response_format = body["response_format"]
        assert response_format["type"] == "json_schema"
        assert response_format["json_schema"]["strict"] is True
        assert response_format["json_schema"]["schema"]["required"] == ["action"]
        user_data = json.loads(body["messages"][1]["content"])
        assert user_data == {
            "text": "Поставь завтра в 19:00 созвон с Колей на полчаса",
            "currentDateTime": "2026-09-26T15:00:00+03:00",
            "locale": "ru-RU",
            "timeZone": "Europe/Moscow",
            "availableConnectors": ["fake-calendar"],
        }
        return model_response(
            {
                "action": {
                    "kind": "calendar.create_event",
                    "connector": "fake-calendar",
                    "payload": {
                        "title": "Созвон с Колей",
                        "startAt": "2026-09-27T19:00:00+03:00",
                        "endAt": "2026-09-27T19:30:00+03:00",
                    },
                    "explanation": "Создать встречу на завтра",
                }
            }
        )

    model = build_model(handle, api_key="test-key")

    reply = await model.propose(
        "Поставь завтра в 19:00 созвон с Колей на полчаса",
        context(),
    )

    assert reply is not None
    assert reply.kind == "calendar.create_event"
    assert reply.payload["title"] == "Созвон с Колей"
    assert reply.payload["timeZone"] == "Europe/Moscow"


@pytest.mark.asyncio
async def test_openai_model_when_reply_has_no_action_should_return_none() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        assert "Authorization" not in request.headers
        return model_response({"action": None})

    model = build_model(handle)

    reply = await model.propose("Привет", context())

    assert reply is None


def build_model(
    handle: Callable[[httpx.Request], httpx.Response],
    *,
    api_key: str | None = None,
) -> OpenAIIntentModel:
    return OpenAIIntentModel(
        base_url="http://model.test/v1",
        model_name="qwen2.5:7b",
        api_key=api_key,
        timeout_seconds=10,
        transport=httpx.MockTransport(handle),
        now=lambda: datetime(2026, 9, 26, 12, 0, tzinfo=UTC),
    )


def model_response(content: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(content, ensure_ascii=False),
                    }
                }
            ]
        },
    )
