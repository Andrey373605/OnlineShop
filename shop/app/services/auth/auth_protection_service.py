import logging

from shop.app.core.config import settings
from shop.app.core.exceptions import PermissionDeniedError
from shop.app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class AuthProtectionService:
    """Сервис защиты от перебора паролей."""

    def __init__(self, cache: CacheService) -> None:
        self._cache = cache

    async def ensure_login_allowed(self, username: str) -> None:
        if await self._cache.is_blacklisted(username):
            raise PermissionDeniedError(
                "Account temporarily blocked due to too many failed login "
                f"attempts. Please try again in {settings.BLOCK_TIME_MINUTES} minutes."
            )

    async def register_failed_attempt(self, username: str) -> None:
        attempts = await self._cache.increment_failed_attempts(username)
        if attempts >= settings.MAX_FAILED_ATTEMPTS:
            await self._cache.add_to_blocklist(
                username=username,
                ttl_minutes=settings.BLOCK_TIME_MINUTES,
            )

    async def reset_failed_attempts(self, username: str) -> None:
        try:
            await self._cache.reset_failed_attempts(username)
        except Exception:
            logger.warning("Failed to reset failed login attempts for '%s'", username)
