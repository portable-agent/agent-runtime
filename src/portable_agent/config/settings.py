from pydantic import AnyHttpUrl, Field
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
