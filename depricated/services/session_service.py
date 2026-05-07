from redis.asyncio import Redis

from shop.app.models.schemas import UserOut
from shop.app.utils.get_utc_now import get_utc_now


class SessionService:
    SESSION_PREFIX = "session:"
    USER_SESSIONS_PREFIX = "user_sessions:"

    def __init__(self, redis_client: Redis, instance_id: str, ttl_seconds: int):
        self._redis = redis_client
        self._instance_id = instance_id
        self._ttl_seconds = ttl_seconds

    def _session_key(self, session_id: str) -> str:
        return f"{self.SESSION_PREFIX}{session_id}"

    def _user_sessions_key(self, user_id: int) -> str:
        return f"{self.USER_SESSIONS_PREFIX}{user_id}"

    @staticmethod
    def _serialize_datetime(value) -> str:
        return value.isoformat()

    async def create_session(
        self,
        user: UserOut,
        session_id: str,
        ip_address: str = "",
        user_agent: str = "",
    ) -> str:
        now = get_utc_now()
        now_iso = self._serialize_datetime(now)

        session_data = {
            "session_id": session_id,
            "user_id": str(user.id),
            "user_data": user.model_dump_json(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": now_iso,
            "last_activity": now_iso,
            "instance_id": self._instance_id,
        }

        key = self._session_key(session_id)
        async with self._redis.pipeline() as pipe:
            pipe.hset(key, mapping=session_data)
            pipe.expire(key, self._ttl_seconds)
            pipe.sadd(self._user_sessions_key(user.id), session_id)
            await pipe.execute()

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        data = await self._redis.hgetall(self._session_key(session_id))
        if not data:
            return None
        return data

    async def get_user_from_session(self, session_id: str) -> UserOut | None:
        user_data = await self._redis.hget(self._session_key(session_id), "user_data")
        if user_data is None:
            return None
        return UserOut.model_validate_json(user_data)

    async def update_activity(self, session_id: str) -> None:
        key = self._session_key(session_id)
        exists = await self._redis.exists(key)
        if not exists:
            return
        now = get_utc_now()
        now_iso = self._serialize_datetime(now)
        async with self._redis.pipeline() as pipe:
            pipe.hset(key, "last_activity", now_iso)
            pipe.expire(key, self._ttl_seconds)
            await pipe.execute()

    async def delete_session(self, session_id: str) -> None:
        key = self._session_key(session_id)
        user_id = await self._redis.hget(key, "user_id")
        async with self._redis.pipeline() as pipe:
            pipe.delete(key)
            if user_id is not None:
                pipe.srem(self._user_sessions_key(int(user_id)), session_id)
            await pipe.execute()

    async def delete_all_user_sessions(self, user_id: int) -> int:
        set_key = self._user_sessions_key(user_id)
        session_ids = await self._redis.smembers(set_key)
        if not session_ids:
            return 0

        async with self._redis.pipeline() as pipe:
            for sid in session_ids:
                pipe.delete(self._session_key(sid))
            pipe.delete(set_key)
            await pipe.execute()

        return len(session_ids)

    async def get_active_sessions(self, user_id: int) -> list[dict]:
        set_key = self._user_sessions_key(user_id)
        session_ids = await self._redis.smembers(set_key)
        if not session_ids:
            return []

        sessions: list[dict] = []
        stale_ids: list[str] = []

        for sid in session_ids:
            data = await self._redis.hgetall(self._session_key(sid))
            if data:
                sessions.append(data)
            else:
                stale_ids.append(sid)

        if stale_ids:
            await self._redis.srem(set_key, *stale_ids)

        return sessions

    async def count_active_sessions(self) -> int:
        count = 0
        async for key in self._redis.scan_iter(
            match=f"{self.SESSION_PREFIX}*", count=200
        ):
            count += 1
        return count
