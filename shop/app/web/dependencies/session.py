from fastapi import Request

from shop.app.core.state import get_app_state
from shop.app.services.session_service import SessionService


async def get_session_service(request: Request) -> SessionService:
    return get_app_state(request).session_service
