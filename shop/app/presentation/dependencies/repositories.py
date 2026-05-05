import asyncpg
from fastapi import Depends

from shop.app.presentation.dependencies.db import get_db
from shop.app.application.interfaces.repositories import UserRepository
from shop.app.infrastructure.persistence.postgres.repositories.user_repository import (
    UserRepositorySql,
)


async def get_user_repository(
    conn: asyncpg.Connection = Depends(get_db),
) -> UserRepository:
    return UserRepositorySql(conn=conn)
