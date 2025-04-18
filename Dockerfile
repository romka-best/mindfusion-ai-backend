FROM python:3.12-slim-bookworm AS base
FROM base AS builder

WORKDIR /app

RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"


EXPOSE 8080
ENV ENVIRONMENT=production
CMD ["uv", "run", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
