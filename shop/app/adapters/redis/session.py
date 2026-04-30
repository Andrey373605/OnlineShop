from redis.asyncio import Redis, RedisError
from shop.app.core.exceptions import StorageUnavailableError
from shop.app.core.ports.session_storage import SessionStoragePort


class RedisSessionStorage(SessionStoragePort):
    def __init__(self, client: Redis):
        self._client = client
        self._user_session_key_prefix = "session:user"

    async def get(self, user_id: int) -> str | None:
        try:
            key = self._user_session_key(user_id)
            result = await self._client.get(key)
            if isinstance(result, bytes):
                return result.decode("utf-8")
            return result
        except RedisError as exc:
            raise StorageUnavailableError("Session storage is temporarily down") from exc

    async def set(self, user_id: int, value: str, ttl_seconds: int) -> None:
        try:
            key = self._user_session_key(user_id)
            await self._client.set(key, value, ex=ttl_seconds)
        except RedisError as exc:
            raise StorageUnavailableError("Failed to save session") from exc

    async def delete(self, user_id: int) -> None:
        try:
            key = self._user_session_key(user_id)
            await self._client.delete(key)
        except RedisError as exc:
            raise StorageUnavailableError("Failed to delete session") from exc

    def _user_session_key(self, user_id: int) -> str:
        return f"{self._user_session_key_prefix}:{user_id}"
