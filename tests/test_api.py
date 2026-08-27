from fastapi.testclient import TestClient

from portable_agent.main import app

client = TestClient(app)


def test_live_returns_up() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_proposal_for_calendar_command_returns_approval_proposal() -> None:
    response = client.post(
        "/api/v1/proposals",
        json={
            "utterance": "Создай встречу с Колей",
            "context": {
                "tenant_id": "8efb312d-5e66-4314-a4ef-d7931932b35a",
                "actor_id": "29e924b6-2c85-4fa1-88ca-dffbde14633b",
                "available_connectors": ["google-calendar"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()["proposal"]
    assert body["kind"] == "calendar.create_event"
    assert body["requires_approval"] is True
