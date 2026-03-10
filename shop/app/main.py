from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from shop.app.api.v1.router import get_api_router
from shop.app.core.config import settings
from shop.app.core.db import create_db_pool, close_db_pool
from shop.app.middlewares.registration import register_middleware
from shop.app.services.cache_service import CacheService, CacheServiceConfig

APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_db_pool()

    cache = CacheService(CacheServiceConfig.from_settings(settings))
    await cache.connect()
    app.state.cache_service = cache

    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.mongo_client = mongo_client

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
