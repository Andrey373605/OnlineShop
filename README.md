# CollabarationSUBD

Backend на `FastAPI` для интернет-витрины и управления каталогом товаров. Проект объединяет каталог, корзину, заказы, отзывы, загрузку изображений, аутентификацию по JWT, журнал событий и аналитику.

Основные данные хранятся в `PostgreSQL`, кеш и сессии работают через `Redis`, журнал событий и аналитика используют `MongoDB`, а медиафайлы сохраняются в `MinIO` (S3-совместимое хранилище).

## Возможности

- JWT-аутентификация с access/refresh токенами и хранением сессий в `Redis`
- каталог товаров: категории, товары, характеристики, изображения
- пользовательские сценарии: корзина, заказы, отзывы
- администрирование пользователей и ролей
- журнал событий в `MongoDB`
- аналитика по событиям
- кеширование справочных и часто запрашиваемых данных
- запуск как локально, так и через `Docker Compose`
- интерактивная документация API через Swagger UI

## Стек

- `Python 3.13+`
- `FastAPI`, `Uvicorn`
- `PostgreSQL`, `asyncpg`, `aiosql`
- `Redis`
- `MongoDB`, `motor`
- `MinIO` / S3 (`aiobotocore`)
- `Pydantic v2`
- `pytest`, `pytest-asyncio`, `httpx`
- `ruff`, `black`, `mypy`
- `uv` для управления зависимостями

## Архитектура

Проект организован по слоям:

- `api` - HTTP-эндпоинты и схемы запросов/ответов
- `api/presenters` и `api/mappers` - представление и преобразование данных для API
- `services` - бизнес-логика
- `repositories` - доступ к данным и репозиторные контракты
- `adapters` - реализации портов для внешних систем (`Redis`, S3/`MinIO`)
- `core/ports` - абстракции (ports) для инфраструктуры и хранилищ
- `infrastructure` - создание/управление клиентами и пулами (`PostgreSQL`, `Redis`, `MongoDB`, `MinIO`)
- `core` - конфигурация, lifespan, обработка ошибок, состояние приложения
- `dependencies` - сборка зависимостей через `Depends`

В приложении используется `Unit of Work` для SQL-операций, `lifespan` для инициализации инфраструктуры и `app.state` для хранения созданных ресурсов.

## Основные маршруты

Базовый префикс API: `/api/v1`

Доступные группы эндпоинтов:

- `auth`
- `analytics`
- `event_logs`
- `categories`
- `products`
- `cart`
- `product_images`
- `product_specifications`
- `roles`
- `users`
- `orders`
- `reviews`

После запуска доступны:

- `GET /` - краткая информация о сервисе
- `GET /health` - проверка состояния приложения
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

## Быстрый старт

### 1. Подготовка окружения

Требуется:

- `Python 3.13+`
- `uv`
- `PostgreSQL`
- `Redis`
- `MongoDB`
- `MinIO`

Создайте `.env` на основе шаблона:

```powershell
Copy-Item .env.example .env
```

Минимально проверьте и заполните:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `MONGODB_USER`
- `MONGODB_PASSWORD`
- `MONGODB_DB`
- `JWT_SECRET_KEY`
- `REDIS_HOST`
- `REDIS_PORT`
- `MINIO_HOST`
- `MINIO_PORT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`

По умолчанию приложение читает настройки из `.env` через `pydantic-settings`.

### 2. Установка зависимостей

```powershell
uv sync
```

### 3. Локальный запуск

Перед запуском убедитесь, что `PostgreSQL`, `Redis`, `MongoDB` и `MinIO` уже доступны.

```powershell
uv run python -m shop.app.main
```

По умолчанию приложение стартует на `http://localhost:8000`, если в `.env` не изменены `APP_HOST` и `APP_PORT`.

Документация API:

- [http://localhost:8000/docs](http://localhost:8000/docs)
- [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Запуск через Docker Compose

Полный стек можно поднять одной командой:

```powershell
docker compose up --build
```

Что запускается:

- `app1`, `app2`, `app3` - три инстанса приложения
- `nginx` - балансировка и внешний вход
- `database` - PostgreSQL
- `redis`
- `mongodb`
- `minio`

Основные точки доступа:

- `http://localhost` - приложение через `nginx`
- `http://localhost:8080` - прямой доступ к `app1`
- `http://localhost:9001` - консоль `MinIO`

## Аутентификация

Проект использует Bearer JWT:

```http
Authorization: Bearer <access_token>
```

Основные auth-эндпоинты:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/sessions`

Swagger UI позволяет удобно получить токен и протестировать защищенные маршруты.

## Проверка качества

Запуск тестов:

```powershell
uv run pytest
```

Проверка линтером:

```powershell
uv run ruff check .
```

Форматирование:

```powershell
uv run black .
```

Проверка типов:

```powershell
uv run mypy .
```

## Структура репозитория

```text
shop/
├── app/
│   ├── api/
│   │   ├── mappers/
│   │   └── presenters/
│   ├── adapters/
│   ├── core/
│   ├── dependencies/
│   ├── infrastructure/
│   ├── middlewares/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── utils/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── guide.md
```

## Примечания

- Для корректной регистрации пользователей роли с идентификаторами `DEFAULT_ADMIN_ROLE_ID` и `DEFAULT_USER_ROLE_ID` должны существовать в базе данных.
- `MongoDB` используется для event logs и аналитики, а не для основных бизнес-данных.
- `Redis` используется не только как кеш, но и для хранения сессий и pub/sub-механизмов.
- `MinIO` отвечает за хранение изображений товаров.
