from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from shop.app.adapters.s3.exceptions import StorageUnavailableError
from shop.app.core.config import settings
from shop.app.core.ports.storage import StorageReadinessPort
from shop.app.core.state import AppState, get_app_state
from shop.app.dependencies.s3 import get_storage_readiness
from shop.app.services.pubsub_service import PubSubChannel, PubSubService
from shop.app.services.session_service import SessionService

APP_VERSION = "1.0.0"

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {
        "message": "Products API",
        "version": APP_VERSION,
        "docs": "/docs",
    }


@router.get("/health/live")
async def live_check() -> dict:
    return {"status": "alive"}


@router.get("/health/ready")
async def ready_check(
    storage: StorageReadinessPort = Depends(get_storage_readiness),
) -> JSONResponse:
    try:
        await storage.ensure_ready()
    except StorageUnavailableError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "dependencies": {
                    "storage": "failed",
                },
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "dependencies": {
                "storage": "ok",
            },
        },
    )


@router.get("/health")
async def health_check(app_state: AppState = Depends(get_app_state)):
    pubsub: PubSubService = app_state.pubsub_service
    session_svc: SessionService = app_state.session_service
    active_sessions = await session_svc.count_active_sessions()

    return {
        "status": "healthy",
        "debug": settings.DEBUG,
        "database": "connected",
        "instance_id": settings.INSTANCE_ID,
        "pubsub": {
            "running": pubsub.is_running,
            "channels": [ch.value for ch in PubSubChannel],
        },
        "sessions": {
            "active_count": active_sessions,
        },
    }
