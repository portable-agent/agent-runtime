from uuid import UUID

from fastapi.testclient import TestClient

from portable_agent.main import create_app
from portable_agent.models.user import TokenUser


class FakeTokenVerifier:
    async def verify(self, token: str) -> TokenUser | None:
        if token != "valid-token":
            return None
        return TokenUser(
            tenant_id=UUID("8efb312d-5e66-4314-a4ef-d7931932b35a"),
            user_id=UUID("29e924b6-2c85-4fa1-88ca-dffbde14633b"),
        )


client = TestClient(create_app(token_verifier=FakeTokenVerifier()))
auth = {"Authorization": "Bearer valid-token"}


def test_live_when_called_without_token_should_return_up() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_app_when_docs_are_disabled_should_not_publish_openapi() -> None:
    safe_client = TestClient(create_app(token_verifier=FakeTokenVerifier(), docs_enabled=False))

    assert safe_client.get("/docs").status_code == 404
    assert safe_client.get("/openapi.json").status_code == 404


def test_app_when_host_is_not_allowed_should_reject_request() -> None:
    safe_client = TestClient(
        create_app(
            token_verifier=FakeTokenVerifier(),
            allowed_hosts=["agent-runtime"],
        )
    )

    response = safe_client.get("/health/live", headers={"Host": "wrong-host"})

    assert response.status_code == 400


def test_create_proposal_without_token_should_return_401() -> None:
    response = client.post("/api/v1/proposals", json=valid_request())

    assert response.status_code == 401


def test_create_proposal_with_invalid_token_should_return_401() -> None:
    response = client.post(
        "/api/v1/proposals",
        headers={"Authorization": "Bearer wrong-token"},
        json=valid_request(),
    )

    assert response.status_code == 401


def test_create_proposal_with_identity_in_body_should_return_422() -> None:
    request = valid_request()
    context = request["context"]
    assert isinstance(context, dict)
    context["tenantId"] = "another-tenant"

    response = client.post("/api/v1/proposals", headers=auth, json=request)

    assert response.status_code == 422


def test_create_proposal_for_incomplete_command_should_return_clarification() -> None:
    response = client.post(
        "/api/v1/proposals",
        headers=auth,
        json={
            "text": "Создай встречу с Колей",
            "context": {"availableConnectors": ["fake-calendar"]},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "proposal": None,
        "clarification": {
            "question": "Укажи название, время начала и время окончания встречи.",
            "missingFields": ["title", "startAt", "endAt"],
        },
    }


def test_create_proposal_for_full_command_should_return_contract_response() -> None:
    response = client.post("/api/v1/proposals", headers=auth, json=valid_request())

    assert response.status_code == 200
    body = response.json()
    assert body["clarification"] is None
    assert body["proposal"]["payload"] == {
        "title": "Обсуждение проекта",
        "startAt": "2026-09-01T12:00:00+03:00",
        "endAt": "2026-09-01T12:30:00+03:00",
        "timeZone": "Europe/Moscow",
    }
    assert body["proposal"]["requiresApproval"] is True
    assert "proposalId" in body["proposal"]


def valid_request() -> dict[str, object]:
    return {
        "text": (
            'Создай встречу "Обсуждение проекта" '
            "с 2026-09-01T12:00:00+03:00 до 2026-09-01T12:30:00+03:00"
        ),
        "context": {
            "timeZone": "Europe/Moscow",
            "availableConnectors": ["fake-calendar"],
        },
    }
