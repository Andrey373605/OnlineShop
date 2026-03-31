import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from shop.app.core.cache import create_cache_service
from shop.app.core.config import settings
from shop.app.services.cache_service import CacheService
from shop.app.core.db import create_db_pool, close_db_pool
from shop.app.core.mongo import create_mongo_client, get_mongo_database, close_mongo_client
from shop.app.core.mongo_indexes import (
    ensure_event_log_search_indexes,
    ensure_event_log_ttl_index,
)
from shop.app.services.pubsub_handlers import (
    make_cache_invalidation_handler,
    make_data_change_handler,
    make_session_invalidation_handler,
)
from shop.app.services.pubsub_service import PubSubChannel, PubSubService
from shop.app.services.session_service import SessionService

logger = logging.getLogger(__name__)


def _create_pubsub_redis() -> Redis:
    """Выделенное Redis-соединение для Pub/Sub (нельзя разделять с data-командами)."""
    return Redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


async def _setup_mongo() -> tuple:
    client = create_mongo_client()
    db = get_mongo_database(client)
    await ensure_event_log_ttl_index(db)
    await ensure_event_log_search_indexes(db)
    return client, db


def _create_session_service(cache_service: CacheService) -> SessionService:
    return SessionService(
        redis_client=cache_service.redis_client,
        instance_id=settings.INSTANCE_ID,
        ttl_seconds=settings.USER_SESSION_CACHE_TTL_SECONDS,
    )


async def _setup_pubsub(
    cache_service: CacheService,
    session_service: SessionService,
) -> tuple[PubSubService, Redis, asyncio.Task]:
    pubsub_service = PubSubService(instance_id=settings.INSTANCE_ID)
    pubsub_redis = _create_pubsub_redis()
    await pubsub_service.connect(pubsub_redis)

    pubsub_service.on(
        PubSubChannel.CACHE_INVALIDATION,
        make_cache_invalidation_handler(cache_service),
    )
    pubsub_service.on(
        PubSubChannel.SESSION_INVALIDATION,
        make_session_invalidation_handler(session_service),
    )
    pubsub_service.on(
        PubSubChannel.DATA_CHANGE,
        make_data_change_handler(),
    )

    await pubsub_service.subscribe_all()
    listener_task = asyncio.create_task(pubsub_service.start_listener())
    return pubsub_service, pubsub_redis, listener_task


async def _close_pubsub(
    pubsub_service: PubSubService,
    pubsub_redis: Redis,
    listener_task: asyncio.Task,
) -> None:
    await pubsub_service.stop()
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass
    await pubsub_redis.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    db_pool = await create_db_pool()
    cache_service = await create_cache_service()
    mongo_client, mongo_db = await _setup_mongo()
    session_service = _create_session_service(cache_service)
    pubsub_service, pubsub_redis, pubsub_task = await _setup_pubsub(
        cache_service, session_service,
    )

    app.state.db_pool = db_pool
    app.state.cache_service = cache_service
    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_db
    app.state.session_service = session_service
    app.state.pubsub_service = pubsub_service

    logger.info(
        "Application started: instance_id=%s, pub/sub channels=%s",
        settings.INSTANCE_ID,
        [ch.value for ch in PubSubChannel],
    )

    yield

    # --- shutdown (обратный порядок) ---
    await _close_pubsub(pubsub_service, pubsub_redis, pubsub_task)
    close_mongo_client(mongo_client)
    await cache_service.disconnect()
    await close_db_pool(db_pool)
