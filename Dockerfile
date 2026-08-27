# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:0.8.15 AS uv
FROM python:3.14-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN uv sync --locked --no-dev

FROM python:3.14-slim
RUN useradd --system --uid 10001 --create-home app
USER 10001
WORKDIR /app
COPY --from=build --chown=10001:10001 /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["uvicorn", "portable_agent.main:app", "--host", "0.0.0.0", "--port", "8080"]
