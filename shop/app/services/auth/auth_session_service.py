import logging

from shop.app.core.exceptions import ServiceUnavailableError
from shop.app.models.schemas import UserOut
from shop.app.services.session_service import SessionService

logger = logging.getLogger(__name__)


class AuthSessionService:
    """Сервис управления сессиями в auth-сценариях."""

    def __init__(self, session_service: SessionService) -> None:
        self._session_service = session_service

    async def create_session(
        self,
        user: UserOut,
        session_id: str,
        ip_address: str = "",
        user_agent: str = "",
    ) -> None:
        await self._session_service.create_session(
            user=user,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def ensure_new_session_created(self, user: UserOut, session_id: str) -> None:
        try:
            await self.create_session(user=user, session_id=session_id)
        except Exception as exc:
            logger.exception("Failed to create new session for user_id=%s", user.id)
            raise ServiceUnavailableError("Unable to rotate user session") from exc

    async def delete_session_if_present(self, session_id: str | None) -> None:
        if not session_id:
            return
        try:
            await self._session_service.delete_session(session_id)
        except Exception:
            logger.warning("Failed to delete old session '%s' after refresh", session_id)

    async def delete_session(self, session_id: str) -> None:
        await self._session_service.delete_session(session_id)
