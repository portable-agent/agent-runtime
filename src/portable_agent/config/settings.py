from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_", extra="ignore")

    oidc_issuer_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8081/realms/portable-agent")
    oidc_jwks_url: AnyHttpUrl = AnyHttpUrl(
        "http://localhost:8081/realms/portable-agent/protocol/openid-connect/certs"
    )
    oidc_audience: str = "agent-runtime"
    allowed_hosts: list[str] = Field(default_factory=lambda: ["127.0.0.1", "localhost"])
    docs_enabled: bool = True
    model_provider: Literal["demo", "openai-compatible"] = "demo"
    model_base_url: AnyHttpUrl = AnyHttpUrl("http://localhost:11434/v1")
    model_name: str = "qwen2.5:7b"
    model_api_key: SecretStr | None = None
    model_timeout_seconds: float = Field(default=30, gt=0, le=120)
