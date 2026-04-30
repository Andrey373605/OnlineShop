import json

from redis import RedisError

from shop.app.core.exceptions import StorageUnavailableError
from shop.app.core.ports.auth_attempt_storage import AuthAttemptStoragePort
from redis.asyncio import Redis


class RedisAuthAttempts(AuthAttemptStoragePort):
    def __init__(self, client: Redis):
        self._client = client
        self._failed_attempts_key_prefix = "auth:attempts"
        self._black_list_key_prefix = "auth:blacklist"

    async def get_failed_attempts(self, username: str) -> int:
        key = self._failed_attempts_key(username)
        try:
            attempts = await self._client.get(key)
            return int(attempts) if attempts else 0
        except RedisError as exc:
            raise StorageUnavailableError("Failed to get auth attempts") from exc

    async def increment_failed_attempts(self, username: str, window_seconds: int) -> int:
        key = self._failed_attempts_key(username)

        try:
            async with self._client.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, window_seconds)
                results = await pipe.execute()
            return results[0]
        except RedisError as exc:
            raise StorageUnavailableError("Failed to increment auth attempts") from exc

    async def reset_failed_attempts(self, username: str) -> None:
        key = self._failed_attempts_key(username)
        try:
            await self._client.delete(key)
        except RedisError as exc:
            raise StorageUnavailableError("Failed to reset auth attempts") from exc

    async def add_to_blocklist(self, username: str, duration_seconds: int) -> None:
        key = self._black_list_key(username)
        payload = json.dumps(
            {
                "username": username,
                "reason": "Too many failed attempts",
            }
        )
        try:
            await self._client.setex(key, duration_seconds, payload)
        except RedisError as exc:
            raise StorageUnavailableError("Failed to add to blocklist") from exc

    async def is_blacklisted(self, username: str) -> bool:
        key = self._black_list_key(username)
        try:
            return bool(await self._client.exists(key))
        except RedisError as exc:
            raise StorageUnavailableError("Failed to check blacklist status") from exc

    def _failed_attempts_key(self, username: str) -> str:
        return f"{self._failed_attempts_key_prefix}:{username}"

    def _black_list_key(self, username: str) -> str:
        return f"{self._black_list_key_prefix}:{username}"
