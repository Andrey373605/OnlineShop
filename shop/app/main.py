from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from shop.app.api.v1 import (
    auth,
    cart,
    categories,
    orders,
    product_images,
    product_specifications,
    products,
    reviews,
    roles,
    users,
)
from shop.app.core.config import settings
from shop.app.core.db import get_db_pool, close_db_pool
from shop.app.services.cache_service import CacheService, CacheServiceConfig

APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_db_pool()

    cache = CacheService(CacheServiceConfig.from_settings(settings))
    await cache.connect()
    app.state.cache_service = cache

    yield

    await cache.disconnect()
    await close_db_pool()

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(product_images.router)
api_router.include_router(product_specifications.router)
api_router.include_router(roles.router)
api_router.include_router(users.router)
api_router.include_router(orders.router)
api_router.include_router(reviews.router)


app = FastAPI(
    title="Products API with Service Layer and aiosql",
    description="API для управления продуктами и категориями",
    version=APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Products API",
        "version": APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "debug": settings.DEBUG,
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "shop.app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
