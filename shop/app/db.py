from typing import Optional
import asyncpg
import aiosql
from shop.app.config import settings

queries = aiosql.from_path("shop/app/queries/", "asyncpg")

_db_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=1,
            max_size=10
        )
    return _db_pool

async def close_db_pool():
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None

async def get_db():
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        yield connection