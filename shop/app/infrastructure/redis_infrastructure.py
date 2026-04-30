from typing import Any

from redis.asyncio import ConnectionPool, Redis

from shop.app.core.ports.base import LifecyclePort
from shop.app.core.ports.pool_provider import PoolProviderPort


class RedisInfrastructure(LifecyclePort, PoolProviderPort):
    def __init__(
        self,
        *,
        url: str,
    ):
        self._url = url
        self._pool: ConnectionPool | None = None

    async def connect(self) -> None:
        self._pool = ConnectionPool.from_url(self._url, decode_responses=True)
        client = Redis(connection_pool=self._pool)
        await client.ping()

    async def close(self) -> None:
        if self._pool:
            await self._pool.disconnect()

    def get_pool(self) -> Any:
        if self._pool is None:
            raise Exception()
        return self._pool
