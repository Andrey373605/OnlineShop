FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock* ./

COPY shop/ ./shop/

RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "shop.app.main"]

