from pathlib import Path

import aiosql
import asyncpg

from shop.app.core.config import settings

_QUERIES_DIR = Path(__file__).resolve().parent.parent / "queries"
queries = aiosql.from_path(_QUERIES_DIR, "asyncpg")


async def create_db_pool() -> asyncpg.Pool:
    """
    Создать пул соединений. Вызывается из lifespan,
    результат хранить в app.state.ext.db_pool.
    """
    return await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=1,
        max_size=10,
    )


async def close_db_pool(pool: asyncpg.Pool) -> None:
    """Закрыть пул. Вызывается из lifespan при остановке приложения."""
    if pool:
        await pool.close()
