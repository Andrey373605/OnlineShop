from redis import RedisError
from redis.asyncio import Redis

from shop.app.core.exceptions import StorageUnavailableError
from shop.app.core.ports.cache_storage import CacheStoragePort


class RedisCacheStorage(CacheStoragePort):
    def __init__(self, client: Redis):
        self._client = client
        self._cache_prefix = "cache"

    async def get_value(self, key: str) -> str | None:
        try:
            return await self._client.get(self._get_key(key))
        except RedisError as exc:
            raise StorageUnavailableError("Cache storage is unavailable") from exc

    async def set_value(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        try:
            full_key = self._get_key(key)
            if ttl_seconds:
                await self._client.setex(full_key, ttl_seconds, value)
            else:
                await self._client.set(full_key, value)
        except RedisError as exc:
            raise StorageUnavailableError("Failed to write to cache") from exc

    async def delete_value(self, key: str) -> None:
        try:
            await self._client.delete(self._get_key(key))
        except RedisError as exc:
            raise StorageUnavailableError("Failed to delete from cache") from exc

    async def delete_value_by_pattern(self, pattern: str) -> None:
        full_pattern = self._get_pattern_key(pattern)
        try:
            async for key_batch in self._batch_scan(full_pattern, count=100):
                if not key_batch:
                    continue
                async with self._client.pipeline(transaction=True) as pipe:
                    for key in key_batch:
                        pipe.delete(key)
                    await pipe.execute()
        except RedisError as exc:
            raise StorageUnavailableError("Failed to clear cache by pattern") from exc

    async def exists_value(self, key: str) -> bool:
        try:
            return bool(await self._client.exists(self._get_key(key)))
        except RedisError as exc:
            raise StorageUnavailableError("Failed to check cache existence") from exc

    async def _batch_scan(self, pattern: str, count: int):
        batch = []
        async for key in self._client.scan_iter(match=pattern, count=count):
            batch.append(key)
            if len(batch) >= count:
                yield batch
                batch = []
        if batch:
            yield batch

    def _get_key(self, key: str) -> str:
        return f"{self._cache_prefix}:{key}"

    def _get_pattern_key(self, pattern: str):
        return f"{self._cache_prefix}:{pattern}"
