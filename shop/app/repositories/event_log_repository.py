from shop.app.schemas.event_log_schemas import EventLogOut


class EventLogRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self, limit: int, offset: int) -> list[EventLogOut]:
        rows = await self.queries.get_all_event_log(
            self.conn,
            limit=limit,
            offset=offset,
        )
        return [EventLogOut(**row) for row in rows]

    async def get_by_id(self, event_id: int) -> EventLogOut | None:
        row = await self.queries.get_event_log_by_id(self.conn, id=event_id)
        return EventLogOut(**row) if row else None

    async def get_by_user_id(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[EventLogOut]:
        rows = await self.queries.get_events_by_user_id(
            self.conn,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return [EventLogOut(**row) for row in rows]

    async def create(self, data: dict) -> int:
        result = await self.queries.create_event_log(self.conn, **data)
        return result["id"]

    async def delete(self, event_id: int) -> bool:
        result = await self.queries.delete_event_log(self.conn, id=event_id)
        return bool(result)


