from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from shop.app.api.v1.router import get_api_router
from shop.app.core.config import settings
from shop.app.core.db import create_db_pool, close_db_pool
from shop.app.core.exception_handlers import register_exception_handlers
from shop.app.core.mongo_indexes import (
    ensure_event_log_search_indexes,
    ensure_event_log_ttl_index,
)
from shop.app.middlewares.registration import register_middleware
from shop.app.repositories.event_log_mongo_repository import EventLogRepositoryMongo
from shop.app.services.cache_service import CacheService, CacheServiceConfig
from shop.app.services.event_log_service import EventLogService

APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_db_pool()

    cache = CacheService(CacheServiceConfig.from_settings(settings))
    await cache.connect()
    app.state.cache_service = cache

    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.mongo_client = mongo_client

    db = mongo_client[settings.MONGODB_DB]
    repo = EventLogRepositoryMongo(db=db)
    app.state.event_log_service = EventLogService(repo=repo)

    await ensure_event_log_ttl_index(db)
    await ensure_event_log_search_indexes(db)

    yield

    mongo_client.close()
    await cache.disconnect()
    await close_db_pool(app.state.db_pool)


def create_app() -> FastAPI:
    new_app = FastAPI(
        title="Products API with Service Layer and aiosql",
        description="API для управления продуктами и категориями",
        version=APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    register_exception_handlers(new_app)
    register_middleware(new_app)
    new_app.include_router(get_api_router())
    return new_app


app = create_app()


@app.get("/")
async def root():
    return {
        "message": "Products API",
        "version": APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "debug": settings.DEBUG,
        "database": "connected",
    }


if __name__ == "__main__":
    import logging
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "shop.app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
