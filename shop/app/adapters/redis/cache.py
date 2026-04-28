from shop.app.core.ports.base import HealthCheckPort, LifecyclePort
from shop.app.core.ports.cache_storage import CacheStoragePort


class RedisCacheStorage(CacheStoragePort, HealthCheckPort, LifecyclePort):

    async def get(self, key: str) -> str | bytes | None:
        pass

    async def delete_pattern(self, key: str) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass

    async def exists(self, key: str) -> bool:
        pass

    async def set(self, key: str, value: str | bytes, ttl_seconds: int | None = None) -> None:
        pass

    async def ensure_ready(self) -> None:
        pass

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass
