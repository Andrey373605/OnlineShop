from dataclasses import dataclass
import json
from typing import List

from redis.asyncio import Redis

from shop.app.core.config import Settings


@dataclass(frozen=True)
class CacheServiceConfig:
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str | None
    block_time_minutes: int
    seconds_in_minute: int

    @classmethod
    def from_settings(cls, settings: Settings) -> "CacheServiceConfig":
        return cls(
            redis_host=settings.REDIS_HOST,
            redis_port=settings.REDIS_PORT,
            redis_db=settings.REDIS_DB,
            redis_password=settings.REDIS_PASSWORD,
            block_time_minutes=settings.BLOCK_TIME_MINUTES,
            seconds_in_minute=settings.SECONDS_IN_MINUTE,
        )


class CacheService:
    def __init__(self, config: CacheServiceConfig):
        self._config = config
        self.redis_client: Redis | None = None

    async def connect(self) -> None:
        self.redis_client = Redis.from_url(
            f'redis://{self._config.redis_host}:{self._config.redis_port}',
            password=self._config.redis_password,
            db=self._config.redis_db,
            decode_responses=True,
        )

    async def delete(self, key: str) -> None:
        self._ensure_connected()
        await self.redis_client.delete(key)

    async def exists(self, key: str) -> bool:
        self._ensure_connected()
        return bool(await self.redis_client.exists(key))

    async def get_list(self, key: str) -> List[str]:
        self._ensure_connected()
        return await self.redis_client.lrange(key, 0, -1)

    async def add_to_list(self, key: str, value: str) -> None:
        self._ensure_connected()
        await self.redis_client.rpush(key, value)

    async def set_list_atomic(
        self,
        key: str,
        items: List[str],
        ttl_seconds: int | None = None,
    ) -> None:
        self._ensure_connected()
        async with self.redis_client.pipeline() as pipe:
            pipe.delete(key)
            if items:
                pipe.rpush(key, *items)
                if ttl_seconds is not None:
                    pipe.expire(key, ttl_seconds)
            await pipe.execute()

    async def get_value(self, key: str) -> str | None:
        """Получить строковое значение по ключу (для JSON и др.)."""
        self._ensure_connected()
        return await self.redis_client.get(key)

    async def set_value(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        """Сохранить строковое значение с опциональным TTL (для кэша аналитики и др.)."""
        self._ensure_connected()
        if ttl_seconds is not None:
            await self.redis_client.setex(key, ttl_seconds, value)
        else:
            await self.redis_client.set(key, value)

    async def disconnect(self) -> None:
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None

    def _ensure_connected(self) -> None:
        if self.redis_client is None:
            raise RuntimeError("CacheService not connected. Call connect() first.")

    async def add_to_blocklist(self, username: str, ttl_minutes: int) -> None:
        self._ensure_connected()
        key = f"blacklist:{username}"
        ttl_seconds = ttl_minutes * self._config.seconds_in_minute
        await self.redis_client.setex(
            key,
            ttl_seconds,
            json.dumps({
                'username': username,
                'blocked_until': ttl_seconds,
                'reason': 'Too many failed attempts'
            })
        )

    async def is_blacklisted(self, username: str) -> bool:
        self._ensure_connected()
        key = f"blacklist:{username}"
        return bool(await self.redis_client.exists(key))

    async def increment_failed_attempts(self, username: str) -> int:
        self._ensure_connected()
        key = f"failed_attempts:{username}"

        attempts = await self.redis_client.incr(key)
        if attempts == 1:
            await self.redis_client.expire(
                key,
                self._config.block_time_minutes * self._config.seconds_in_minute
            )

        return attempts

    async def get_failed_attempts(self, username: str) -> int:
        self._ensure_connected()
        key = f"failed_attempts:{username}"
        attempts = await self.redis_client.get(key)
        return int(attempts) if attempts else 0

    async def reset_failed_attempts(self, username: str) -> None:
        self._ensure_connected()
        key = f"failed_attempts:{username}"
        await self.redis_client.delete(key)

