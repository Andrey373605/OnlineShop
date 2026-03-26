import asyncpg
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from shop.app.core.db import queries
from shop.app.dependencies.db import get_db
from shop.app.dependencies.mongo import get_mongo_db
from shop.app.repositories.event_log_mongo_repository import EventLogRepositoryMongo
from shop.app.repositories.protocols import EventLogRepository, UserRepository
from shop.app.repositories.user_repository import UserRepositorySql


async def get_user_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> UserRepository:
    """Используется только в ``get_current_user`` (JWT-проверка), где полный UoW не нужен."""
    return UserRepositorySql(conn=conn, queries=queries)


async def get_event_log_repository(
    db: AsyncIOMotorDatabase = Depends(get_mongo_db),
) -> EventLogRepository:
    return EventLogRepositoryMongo(db=db)
