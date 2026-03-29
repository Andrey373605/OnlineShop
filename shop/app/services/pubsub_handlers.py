import logging

from shop.app.services.cache_service import CacheService
from shop.app.services.session_service import SessionService

logger = logging.getLogger(__name__)


def make_cache_invalidation_handler(cache: CacheService):
    async def handle(message: dict) -> None:
        pattern = message.get("pattern")
        key = message.get("key")

        if pattern:
            deleted = await cache.delete_by_pattern(pattern)
            logger.info(
                "Cache invalidation via pub/sub: pattern=%s, deleted=%d, from=%s",
                pattern,
                deleted,
                message.get("instance_id"),
            )
        elif key:
            await cache.delete(key)
            logger.info(
                "Cache invalidation via pub/sub: key=%s, from=%s",
                key,
                message.get("instance_id"),
            )

    return handle


def make_session_invalidation_handler(session_service: SessionService):
    async def handle(message: dict) -> None:
        session_id = message.get("session_id")
        user_id = message.get("user_id")

        if session_id:
            await session_service.delete_session(session_id)
            logger.info(
                "Session invalidated via pub/sub: session=%s, from=%s",
                session_id,
                message.get("instance_id"),
            )
        elif user_id is not None:
            count = await session_service.delete_all_user_sessions(int(user_id))
            logger.info(
                "All sessions invalidated via pub/sub: user=%s, count=%d, from=%s",
                user_id,
                count,
                message.get("instance_id"),
            )

    return handle


def make_data_change_handler():
    async def handle(message: dict) -> None:
        logger.info(
            "Data change notification: entity=%s, action=%s, from=%s",
            message.get("entity"),
            message.get("action"),
            message.get("instance_id"),
        )

    return handle
