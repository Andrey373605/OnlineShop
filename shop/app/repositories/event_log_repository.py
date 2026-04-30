from datetime import datetime

from shop.app.models.schemas import EventLogOut
from shop.app.repositories.protocols import EventLogRepository


class EventLogRepositorySql(EventLogRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[EventLogOut]:
        rows = await self._conn.fetch(
            """
            SELECT id, event_type, user_id, description, ip_address, user_agent, created_at
            FROM event_log
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return [EventLogOut(**row) for row in rows]

    async def get_by_id(self, event_id: int) -> EventLogOut | None:
        row = await self._conn.fetchrow(
            """
            SELECT id, event_type, user_id, description, ip_address, user_agent, created_at
            FROM event_log
            WHERE id = $1;
            """,
            event_id,
        )
        return EventLogOut(**row) if row else None

    async def get_by_user_id(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[EventLogOut]:
        rows = await self._conn.fetch(
            """
            SELECT id, event_type, user_id, description, ip_address, user_agent, created_at
            FROM event_log
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
            """,
            user_id,
            limit,
            offset,
        )
        return [EventLogOut(**row) for row in rows]

    async def get_filtered(
        self,
        *,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        user_id: int | None = None,
        event_type: str | None = None,
        limit: int,
        offset: int,
    ) -> tuple[list[EventLogOut], int]:
        # Заглушка: полная фильтрация реализована в EventLogRepositoryMongo.
        if user_id is not None:
            rows = await self._conn.fetch(
                """
                SELECT id, event_type, user_id, description, ip_address, user_agent, created_at
                FROM event_log
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3;
                """,
                user_id,
                limit,
                offset,
            )
            items = [EventLogOut(**row) for row in rows]
        else:
            items = await self.get_all(limit=limit, offset=offset)
        return items, 0  # total не поддерживается без отдельного COUNT-запроса

    _CREATE_KEYS = ("event_type", "user_id", "description", "ip_address", "user_agent")

    async def create(self, data: dict) -> int:
        filtered = {k: data[k] for k in self._CREATE_KEYS if k in data}
        result = await self._conn.fetchrow(
            """
            INSERT INTO event_log (event_type, user_id, description, ip_address, user_agent)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id;
            """,
            filtered.get("event_type"),
            filtered.get("user_id"),
            filtered.get("description"),
            filtered.get("ip_address"),
            filtered.get("user_agent"),
        )
        return result["id"]

    async def delete(self, event_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM event_log WHERE id = $1 RETURNING id;",
            event_id,
        )
        return bool(result)
