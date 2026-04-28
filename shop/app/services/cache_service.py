import json
from dataclasses import dataclass

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
        self._redis_client: Redis | None = None

    @property
    def redis_client(self) -> Redis:
        if self._redis_client is None:
            raise RuntimeError("CacheService not connected. Call connect() first.")
        return self._redis_client

    async def connect(self) -> None:
        self._redis_client = Redis.from_url(
            f"redis://{self._config.redis_host}:{self._config.redis_port}",
            password=self._config.redis_password,
            db=self._config.redis_db,
            decode_responses=True,
        )

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)

    async def delete_by_pattern(self, pattern: str) -> int:
        deleted = 0
        async for key in self.redis_client.scan_iter(match=pattern, count=100):
            await self.redis_client.delete(key)
            deleted += 1
        return deleted

    async def exists(self, key: str) -> bool:
        return bool(await self.redis_client.exists(key))

    async def get_list(self, key: str) -> list[str]:
        return await self.redis_client.lrange(key, 0, -1)

    async def add_to_list(self, key: str, value: str) -> None:
        await self.redis_client.rpush(key, value)

    async def set_list_atomic(
        self,
        key: str,
        items: list[str],
        ttl_seconds: int | None = None,
    ) -> None:
        async with self.redis_client.pipeline() as pipe:
            pipe.delete(key)
            if items:
                pipe.rpush(key, *items)
                if ttl_seconds is not None:
                    pipe.expire(key, ttl_seconds)
            await pipe.execute()

    async def get_value(self, key: str) -> str | None:
        return await self.redis_client.get(key)

    async def set_value(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        if ttl_seconds is not None:
            await self.redis_client.setex(key, ttl_seconds, value)
        else:
            await self.redis_client.set(key, value)

    def _user_session_key(self, user_id: int) -> str:
        return f"session:user:{user_id}"

    async def get_user_session(self, user_id: int) -> str | None:
        return await self.get_value(self._user_session_key(user_id))

    async def set_user_session(self, user_id: int, value: str, ttl_seconds: int) -> None:
        await self.set_value(self._user_session_key(user_id), value, ttl_seconds=ttl_seconds)

    async def delete_user_session(self, user_id: int) -> None:
        await self.delete(self._user_session_key(user_id))

    async def disconnect(self) -> None:
        if self.redis_client:
            await self.redis_client.aclose()
            self._redis_client = None

    async def add_to_blocklist(self, username: str, ttl_minutes: int) -> None:
        key = f"blacklist:{username}"
        ttl_seconds = ttl_minutes * self._config.seconds_in_minute
        await self.redis_client.setex(
            key,
            ttl_seconds,
            json.dumps(
                {
                    "username": username,
                    "blocked_until": ttl_seconds,
                    "reason": "Too many failed attempts",
                }
            ),
        )

    async def is_blacklisted(self, username: str) -> bool:
        key = f"blacklist:{username}"
        return bool(await self.redis_client.exists(key))

    async def increment_failed_attempts(self, username: str) -> int:
        key = f"failed_attempts:{username}"

        attempts = await self.redis_client.incr(key)
        if attempts == 1:
            await self.redis_client.expire(
                key, self._config.block_time_minutes * self._config.seconds_in_minute
            )

        return attempts

    async def get_failed_attempts(self, username: str) -> int:
        key = f"failed_attempts:{username}"
        attempts = await self.redis_client.get(key)
        return int(attempts) if attempts else 0

    async def reset_failed_attempts(self, username: str) -> None:
        key = f"failed_attempts:{username}"
        await self.redis_client.delete(key)
