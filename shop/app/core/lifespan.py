import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from shop.app.adapters.s3.storage import S3Storage

from shop.app.core.config import settings


from shop.app.infrastructure.minio_infrastructure import MinioInfrastructure
from shop.app.infrastructure.mongo_infrastructure import MongoInfrastructure
from shop.app.infrastructure.postgres_infrastructure import PostgresInfrastructure
from shop.app.infrastructure.redis_infrastructure import RedisInfrastructure
from shop.app.services.cache_service import CacheService
from shop.app.services.pubsub_handlers import (
    make_cache_invalidation_handler,
    make_data_change_handler,
    make_session_invalidation_handler,
)
from shop.app.services.pubsub_service import PubSubChannel, PubSubService
from shop.app.services.session_service import SessionService

logger = logging.getLogger(__name__)


def create_postgres_infrastructure() -> PostgresInfrastructure:
    return PostgresInfrastructure(
        url=settings.DATABASE_URL,
        min_size=settings.POSTGRES_MIN_POOL_SIZE,
        max_size=settings.POSTGRES_MAX_POOL_SIZE,
    )


def create_mongo_infrastructure() -> MongoInfrastructure:
    return MongoInfrastructure(url=settings.MONGO_URL)


def create_redis_infrastructure() -> RedisInfrastructure:
    return RedisInfrastructure(url=settings.REDIS_URL)


def create_minio_infrastructure() -> MinioInfrastructure:
    return MinioInfrastructure(
        endpoint_url=settings.MINIO_URL,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
    )


def create_storage(minio: MinioInfrastructure) -> S3Storage:
    return S3Storage(client=minio.get_client(), bucket_name=settings.MINIO_BUCKET)


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
    # postgres
    postgres = create_postgres_infrastructure()
    await postgres.connect()

    # redis
    redis = create_redis_infrastructure()
    await redis.connect()

    # mongo
    mongo = create_mongo_infrastructure()
    mongo.connect()

    # S3 infrastructure + adapters
    minio = create_minio_infrastructure()
    await minio.connect()

    storage = create_storage(minio)
    # await storage.ensure_ready()

    # app.state.ext = AppState(
    #     db_pool=db_pool,
    #     cache_service=cache_service,
    #     mongo_client=mongo_client,
    #     mongo_db=mongo_db,
    #     session_service=session_service,
    #     pubsub_service=pubsub_service,
    #     storage=storage,
    #     storage_readiness=storage,
    # )

    logger.info(
        "Application started: instance_id=%s, pub/sub channels=%s",
        settings.INSTANCE_ID,
        [ch.value for ch in PubSubChannel],
    )

    yield

    # --- shutdown ---

    await minio.close()
    mongo.close()
    await redis.close()
    await postgres.close()
