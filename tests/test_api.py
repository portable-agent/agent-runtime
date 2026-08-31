from fastapi.testclient import TestClient

from portable_agent.main import create_app

client = TestClient(create_app())


def test_live_returns_up() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_proposal_for_incomplete_calendar_command_returns_clarification() -> None:
    response = client.post(
        "/api/v1/proposals",
        json={
            "utterance": "Создай встречу с Колей",
            "context": {
                "tenant_id": "8efb312d-5e66-4314-a4ef-d7931932b35a",
                "actor_id": "29e924b6-2c85-4fa1-88ca-dffbde14633b",
                "available_connectors": ["fake-calendar"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["proposal"] is None
    assert body["clarification"] == {
        "question": "Укажи название, время начала и время окончания встречи.",
        "missing_fields": ["title", "startAt", "endAt"],
    }


def test_create_proposal_for_full_demo_command_returns_approval_proposal() -> None:
    response = client.post(
        "/api/v1/proposals",
        json={
            "utterance": (
                'Создай встречу "Обсуждение проекта" '
                "с 2026-09-01T12:00:00+03:00 до 2026-09-01T12:30:00+03:00"
            ),
            "context": {
                "tenant_id": "8efb312d-5e66-4314-a4ef-d7931932b35a",
                "actor_id": "29e924b6-2c85-4fa1-88ca-dffbde14633b",
                "timezone": "Europe/Moscow",
                "available_connectors": ["fake-calendar"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["clarification"] is None
    assert body["proposal"]["payload"] == {
        "title": "Обсуждение проекта",
        "startAt": "2026-09-01T12:00:00+03:00",
        "endAt": "2026-09-01T12:30:00+03:00",
        "timeZone": "Europe/Moscow",
    }
    assert body["proposal"]["requires_approval"] is True
