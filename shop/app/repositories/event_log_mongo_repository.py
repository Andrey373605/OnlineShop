from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from shop.app.core.config import settings
from shop.app.schemas.event_log_schemas import EventLogOut


def _event_log_now() -> datetime:
    """Момент записи лога в настроенном часовом поясе (в BSON уходит тот же инстант в UTC)."""
    return datetime.now(timezone.utc)


def _created_at_for_api(dt: datetime) -> datetime:
    """Mongo отдаёт UTC (часто без tzinfo); для API — в EVENT_LOG_TIMEZONE."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(settings.event_log_tz)


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
        self._db = db

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self._db["event_log"]

    @property
    def counter_collection(self) -> AsyncIOMotorCollection:
        return self._db["counter_collection"]

    def _to_out(self, doc: dict) -> EventLogOut:
        data = {k: v for k, v in doc.items() if k != "_id"}
        if (ca := data.get("created_at")) is not None:
            data["created_at"] = _created_at_for_api(ca)
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

    async def get_next_id(self, counter_name: str):
        result = await self.counter_collection.find_one_and_update(
            {"_id": counter_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return result["seq"]

    async def create(self, data: dict) -> int:
        next_id = await self.get_next_id("entity_id")
        data["id"] = next_id
        data.setdefault("created_at", _event_log_now())
        await self.collection.insert_one(data)
        return next_id

    async def delete(self, event_id: int) -> bool:
        result = await self.collection.delete_one({"id": event_id})
        return result.deleted_count > 0
