from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from shop.app.schemas.event_log_schemas import EventLogOut


def _build_filter_query(
    *,
    time_from: datetime | None = None,
    time_to: datetime | None = None,
    user_id: int | None = None,
    event_type: str | None = None,
) -> dict:
    """Собирает MongoDB-запрос по опциональным фильтрам."""
    query: dict = {}
    if time_from is not None or time_to is not None:
        query["created_at"] = {}
        if time_from is not None:
            query["created_at"]["$gte"] = time_from
        if time_to is not None:
            query["created_at"]["$lte"] = time_to
    if user_id is not None:
        query["user_id"] = user_id
    if event_type is not None:
        query["event_type"] = event_type
    return query


class EventLogRepositoryMongo:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self.db["event_log"]

    def _to_out(self, doc: dict) -> EventLogOut:
        data = {k: v for k, v in doc.items() if k != "_id"}
        return EventLogOut(**data)

    async def get_all(self, limit: int, offset: int) -> list[EventLogOut]:
        cursor = self.collection.find().skip(offset).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._to_out(d) for d in docs]

    async def get_by_id(self, event_id: int) -> EventLogOut | None:
        doc = await self.collection.find_one({"id": event_id})
        return self._to_out(doc) if doc else None

    async def get_by_user_id(
        self, user_id: int, limit: int, offset: int
    ) -> list[EventLogOut]:
        cursor = (
            self.collection.find({"user_id": user_id}).skip(offset).limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_out(d) for d in docs]

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
        query = _build_filter_query(
            time_from=time_from,
            time_to=time_to,
            user_id=user_id,
            event_type=event_type,
        )
        total = await self.collection.count_documents(query)
        cursor = (
            self.collection.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._to_out(d) for d in docs], total

    async def create(self, data: dict) -> int:
        cursor = self.collection.find().sort("id", -1).limit(1)
        last = await cursor.to_list(length=1)
        next_id = (last[0]["id"] + 1) if last else 1
        data["id"] = next_id
        data.setdefault("created_at", datetime.now(timezone.utc))
        await self.collection.insert_one(data)
        return next_id

    async def delete(self, event_id: int) -> bool:
        result = await self.collection.delete_one({"id": event_id})
        return result.deleted_count > 0
