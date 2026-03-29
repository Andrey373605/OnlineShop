import logging

from fastapi import FastAPI

from shop.app.api.health import router as health_router
from shop.app.api.v1.router import get_api_router
from shop.app.core.config import settings
from shop.app.core.exception_handlers import register_exception_handlers
from shop.app.core.lifespan import lifespan
from shop.app.middlewares.registration import register_middleware

logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    new_app = FastAPI(
        title="Products API with Service Layer and aiosql",
        description="API для управления продуктами и категориями",
        version="1.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    register_exception_handlers(new_app)
    register_middleware(new_app)
    new_app.include_router(health_router)
    new_app.include_router(get_api_router())
    return new_app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "shop.app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
