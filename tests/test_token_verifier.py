import time
from typing import Any
from uuid import UUID

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from portable_agent.config.token_verifier import OidcTokenVerifier


@pytest.mark.asyncio
async def test_verify_when_token_is_valid_should_return_identity(monkeypatch: Any) -> None:
    verifier, token = signed_token(monkeypatch)

    user = await verifier.verify(token)

    assert user is not None
    assert user.tenant_id == UUID("8efb312d-5e66-4314-a4ef-d7931932b35a")
    assert user.user_id == UUID("29e924b6-2c85-4fa1-88ca-dffbde14633b")


@pytest.mark.asyncio
async def test_verify_when_audience_is_wrong_should_reject_token(monkeypatch: Any) -> None:
    verifier, token = signed_token(monkeypatch, audience="another-service")

    assert await verifier.verify(token) is None


@pytest.mark.asyncio
async def test_verify_when_tenant_is_missing_should_reject_token(monkeypatch: Any) -> None:
    verifier, token = signed_token(monkeypatch, include_tenant=False)

    assert await verifier.verify(token) is None


def signed_token(
    monkeypatch: Any,
    *,
    audience: str = "agent-runtime",
    include_tenant: bool = True,
) -> tuple[OidcTokenVerifier, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issuer = "http://localhost:8081/realms/portable-agent"
    claims: dict[str, object] = {
        "sub": "29e924b6-2c85-4fa1-88ca-dffbde14633b",
        "iss": issuer,
        "aud": audience,
        "iat": int(time.time()),
        "exp": int(time.time()) + 300,
    }
    if include_tenant:
        claims["tenant_id"] = "8efb312d-5e66-4314-a4ef-d7931932b35a"
    token = jwt.encode(claims, private_key, algorithm="RS256")
    verifier = OidcTokenVerifier(
        issuer=issuer,
        jwks_url=f"{issuer}/protocol/openid-connect/certs",
        audience="agent-runtime",
    )

    class SigningKey:
        key = private_key.public_key()

    monkeypatch.setattr(
        verifier._key_client,
        "get_signing_key_from_jwt",
        lambda _token: SigningKey(),
    )
    return verifier, token
