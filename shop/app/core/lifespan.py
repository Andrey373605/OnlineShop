from contextlib import asynccontextmanager

from fastapi import FastAPI

from shop.app.infrastructure.services.storage.s3_storage import S3Storage

from shop.app.core.config import settings


from shop.app.infrastructure.services.storage.connection import MinioInfrastructure
from shop.app.infrastructure.persistence.postgres.connection import (
    PostgresInfrastructure,
)


def create_postgres_infrastructure() -> PostgresInfrastructure:
    return PostgresInfrastructure(
        url=settings.DATABASE_URL,
        min_size=settings.POSTGRES_MIN_POOL_SIZE,
        max_size=settings.POSTGRES_MAX_POOL_SIZE,
    )


def create_minio_infrastructure() -> MinioInfrastructure:
    return MinioInfrastructure(
        endpoint_url=settings.MINIO_URL,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
    )


def create_storage(minio: MinioInfrastructure) -> S3Storage:
    return S3Storage(client=minio.get_client(), bucket_name=settings.MINIO_BUCKET)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # postgres
    postgres = create_postgres_infrastructure()
    await postgres.connect()

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
    #     storage=storage,
    #     storage_readiness=storage,
    # )

    yield

    # --- shutdown ---

    await minio.close()
    await postgres.close()
