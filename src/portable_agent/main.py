from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from portable_agent.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    del app
    yield


app = FastAPI(
    title="Portable Agent Runtime",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/health/live", include_in_schema=False)
async def live() -> dict[str, str]:
    return {"status": "UP"}
