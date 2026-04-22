from fastapi import APIRouter, Depends

from shop.app.core.config import settings
from shop.app.core.state import AppState, get_app_state
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
