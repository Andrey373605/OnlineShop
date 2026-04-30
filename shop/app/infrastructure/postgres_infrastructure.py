import asyncpg

from shop.app.core.ports.base import LifecyclePort
from shop.app.core.ports.pool_provider import PoolProviderPort


class PostgresInfrastructure(LifecyclePort, PoolProviderPort):
    def __init__(self, *, url: str, min_size: int, max_size: int):
        self._url = url
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is not None:
            return
        await asyncpg.create_pool(
            dsn=self._url,
            min_size=self._min_size,
            max_size=self._max_size,
        )

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Postgres pool is not connected")
        return self._pool
