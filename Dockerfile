FROM python:3.13-slim

WORKDIR /app

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Копируем зависимости и lock файл
COPY pyproject.toml uv.lock* ./

# Копируем исходный код
COPY shop/ ./shop/

# Устанавливаем зависимости
RUN uv sync --frozen

# Запускаем приложение
CMD ["uv", "run", "python", "-m", "shop.app.main"]

