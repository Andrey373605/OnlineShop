from datetime import datetime

from shop.app.schemas.event_log_schemas import EventLogOut


class EventLogRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_all(self, limit: int, offset: int) -> list[EventLogOut]:
        rows = await self._queries.get_all_event_log(
            self._conn,
            limit=limit,
            offset=offset,
        )
        return [EventLogOut(**row) for row in rows]

    async def get_by_id(self, event_id: int) -> EventLogOut | None:
        row = await self._queries.get_event_log_by_id(self._conn, id=event_id)
        return EventLogOut(**row) if row else None

    async def get_by_user_id(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[EventLogOut]:
        rows = await self._queries.get_events_by_user_id(
            self._conn,
            user_id=user_id,
            limit=limit,
            offset=offset,
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
        # При использовании SQL можно добавить соответствующие запросы в queries.
        if user_id is not None:
            rows = await self._queries.get_events_by_user_id(
                self._conn, user_id=user_id, limit=limit, offset=offset
            )
            items = [EventLogOut(**row) for row in rows]
        else:
            items = await self.get_all(limit=limit, offset=offset)
        return items, 0  # total не поддерживается без отдельного COUNT-запроса

    _CREATE_KEYS = ("event_type", "user_id", "description", "ip_address", "user_agent")

    async def create(self, data: dict) -> int:
        filtered = {k: data[k] for k in self._CREATE_KEYS if k in data}
        result = await self._queries.create_event_log(self._conn, **filtered)
        return result["id"]

    async def delete(self, event_id: int) -> bool:
        result = await self._queries.delete_event_log(self._conn, id=event_id)
        return bool(result)


