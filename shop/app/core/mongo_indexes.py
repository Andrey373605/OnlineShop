import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from shop.app.core.config import settings

logger = logging.getLogger(__name__)


async def ensure_event_log_ttl_index(db: AsyncIOMotorDatabase) -> None:
    """
    Гарантирует наличие TTL-индекса для коллекции event_log.

    TTL хранится в настройке settings.EVENT_LOG_TTL_DAYS.
    Если индекс уже существует новый индекс не будет создаваться
    IndexOptionsConflict — в этом случае мы логируем предупреждение
    и не падаем при старте приложения (ожидается ручная миграция).
    """

    logger.info("Ensuring TTL index on event_log collection")
    collection = db["event_log"]

    index_name = "event_log_created_at_ttl"
    async for index in collection.list_indexes():
        if index['name'] == index_name:
            logger.info(f"TTL index '{index_name}' on event_log collection already exists")
            return

    ttl_seconds = settings.EVENT_LOG_TTL_DAYS * 24 * 60 * 60
    try:
        await collection.create_index(
            "created_at",
            expireAfterSeconds=ttl_seconds,
            name=index_name,
            background=True,
        )
    except Exception as exc:
        logger.warning("Failed to ensure TTL index on event_log: %s", exc)


async def ensure_event_log_search_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Индексы для быстрой фильтрации логов по временному интервалу, пользователю и типу события.
    """
    logger.info("Ensuring search indexes on event_log collection")
    collection = db["event_log"]
    index_name = "event_log_search"
    async for index in collection.list_indexes():
        if index["name"] == index_name:
            logger.info("Search index '%s' on event_log collection already exists", index_name)
            return
    try:
        await collection.create_index(
            [("created_at", -1), ("user_id", 1), ("event_type", 1)],
            name=index_name,
            background=True,
        )
        logger.info("Created search index '%s' on event_log collection", index_name)
    except Exception as exc:
        logger.warning("Failed to ensure search index on event_log: %s", exc)

