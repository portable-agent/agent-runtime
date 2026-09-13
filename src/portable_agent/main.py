from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from portable_agent.config.settings import Settings
from portable_agent.config.token_verifier import OidcTokenVerifier, TokenVerifier
from portable_agent.controllers.proposal_controller import build_router


def create_app(
    token_verifier: TokenVerifier,
    *,
    allowed_hosts: list[str] | None = None,
    docs_enabled: bool = True,
) -> FastAPI:
    docs_url = "/docs" if docs_enabled else None
    app = FastAPI(
        title="Portable Agent Runtime",
        version="2.1.0",
        docs_url=docs_url,
        redoc_url=None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts or ["testserver"],
    )
    app.include_router(build_router(token_verifier))

    @app.get("/health/live", include_in_schema=False)
    async def live() -> dict[str, str]:
        return {"status": "UP"}

    return app


settings = Settings()
app = create_app(
    OidcTokenVerifier(
        issuer=str(settings.oidc_issuer_url),
        jwks_url=str(settings.oidc_jwks_url),
        audience=settings.oidc_audience,
    ),
    allowed_hosts=settings.allowed_hosts,
    docs_enabled=settings.docs_enabled,
)
