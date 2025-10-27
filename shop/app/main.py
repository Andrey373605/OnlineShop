from contextlib import asynccontextmanager
from fastapi import FastAPI

from shop.app.api.v1 import categories, products
from shop.app.core.config import settings
from shop.app.core.db import get_db_pool, close_db_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_db_pool()
    yield
    await close_db_pool()


app = FastAPI(
    title="Products API with Service Layer and aiosql",
    description="API для управления продуктами и категориями",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

app.include_router(categories.router)
app.include_router(products.router)


# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Products API",
        "version": "1.0.0",
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
