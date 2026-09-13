from pathlib import Path
from typing import Any
from uuid import UUID

import yaml
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

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


def test_api_when_request_and_response_are_valid_should_match_contract() -> None:
    contract = read_contract()
    request = valid_request()
    validate(request, "ProposalRequest", contract)

    client = TestClient(create_app(token_verifier=FakeTokenVerifier()))
    response = client.post(
        "/api/v1/proposals",
        headers={"Authorization": "Bearer valid-token"},
        json=request,
    )

    assert response.status_code == 200
    validate(response.json(), "ProposalResponse", contract)


def test_contract_version_should_be_2_1_0() -> None:
    assert read_contract()["info"]["version"] == "2.1.0"


def read_contract() -> dict[str, Any]:
    contract_path = Path(__file__).parents[1] / "contracts" / "agent-runtime-api.yaml"
    data = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def validate(
    value: object,
    schema_name: str,
    contract: dict[str, Any],
) -> None:
    resource = Resource.from_contents(
        {"$schema": "https://json-schema.org/draft/2020-12/schema", **contract}
    )
    registry = Registry().with_resource("urn:agent-runtime", resource)
    Draft202012Validator(
        {"$ref": f"urn:agent-runtime#/components/schemas/{schema_name}"},
        registry=registry,
        format_checker=FormatChecker(),
    ).validate(value)


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
