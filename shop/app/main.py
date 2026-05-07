from fastapi import FastAPI

from shop.app.presentation.fastapi.routers.health import router as health_router
from shop.app.presentation.fastapi.routers import get_api_router
from shop.app.core.config import settings
from shop.app.core.exception_handlers import setup_exception_handlers
from shop.app.core.lifespan import lifespan
from shop.app.presentation.core.registration import setup_middleware


def create_app() -> FastAPI:
    new_app = FastAPI(
        title="Products API with Service Layer and aiosql",
        description="API для управления продуктами и категориями",
        version="1.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    setup_exception_handlers(new_app)
    setup_middleware(new_app)
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
