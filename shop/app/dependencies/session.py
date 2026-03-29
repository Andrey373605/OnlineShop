from fastapi import Request

from shop.app.services.session_service import SessionService


async def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service
