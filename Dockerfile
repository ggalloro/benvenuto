FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY app ./app
COPY policies ./policies

# The SQLite file is created and seeded on first request (ephemeral on Cloud Run).
ENV BENVENUTO_DB=/tmp/benvenuto.db PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips '*'"]
