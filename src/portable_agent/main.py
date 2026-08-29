from fastapi import FastAPI

from portable_agent.controllers.proposal_controller import router


def create_app() -> FastAPI:
    app = FastAPI(title="Portable Agent Runtime", version="0.1.0", docs_url="/docs")
    app.include_router(router)

    @app.get("/health/live", include_in_schema=False)
    async def live() -> dict[str, str]:
        return {"status": "UP"}

    return app


app = create_app()
