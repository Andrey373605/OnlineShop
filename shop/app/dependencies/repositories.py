import asyncpg
from fastapi import Depends

from shop.app.dependencies.db import get_db
from shop.app.repositories.protocols import UserRepository
from shop.app.repositories.user_repository import UserRepositorySql


async def get_user_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> UserRepository:
    return UserRepositorySql(conn=conn)
