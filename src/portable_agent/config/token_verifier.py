import asyncio
from typing import Any, Protocol
from uuid import UUID

import jwt

from portable_agent.models.user import TokenUser


class TokenVerifier(Protocol):
    async def verify(self, token: str) -> TokenUser | None: ...


class OidcTokenVerifier:
    def __init__(self, *, issuer: str, jwks_url: str, audience: str) -> None:
        self._issuer = issuer.rstrip("/")
        self._audience = audience
        self._key_client = jwt.PyJWKClient(jwks_url)

    async def verify(self, token: str) -> TokenUser | None:
        try:
            claims = await asyncio.to_thread(self._read_claims, token)
            return TokenUser(
                tenant_id=UUID(self._text_claim(claims, "tenant_id")),
                user_id=UUID(self._text_claim(claims, "sub")),
            )
        except jwt.PyJWTError, KeyError, TypeError, ValueError:
            return None

    def _read_claims(self, token: str) -> dict[str, Any]:
        key = self._key_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iat", "iss", "sub", "aud", "tenant_id"]},
        )

    @staticmethod
    def _text_claim(claims: dict[str, Any], name: str) -> str:
        value = claims[name]
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} must be a non-empty string")
        return value
