from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from shop.app.repositories.protocols import EventLogAnalyticsRepository


class EventLogAnalyticsRepositoryMongo(EventLogAnalyticsRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self._db["event_log"]

    async def aggregate_activity_by_period(
        self,
        period: str,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
    ) -> list[dict]:
        match_stage: dict = {}
        if time_from or time_to:
            match_stage["created_at"] = {}
            if time_from:
                match_stage["created_at"]["$gte"] = time_from
            if time_to:
                match_stage["created_at"]["$lte"] = time_to
        pipeline: list[dict] = []
        if match_stage:
            pipeline.append({"$match": match_stage})
        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": {"$dateTrunc": {"date": "$created_at", "unit": period}},
                        "event_count": {"$sum": 1},
                        "unique_users": {"$addToSet": "$user_id"},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "period": "$_id",
                        "event_count": 1,
                        "unique_users": {"$size": "$unique_users"},
                    }
                },
                {"$sort": {"period": 1}},
            ]
        )
        return await self.collection.aggregate(pipeline).to_list(length=None)

    async def aggregate_top_users(self, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"user_id": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$user_id",
                    "event_count": {"$sum": 1},
                    "last_activity": {"$max": "$created_at"},
                    "event_types": {"$addToSet": "$event_type"},
                }
            },
            {"$sort": {"event_count": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "user_id": "$_id",
                    "event_count": 1,
                    "last_activity": 1,
                    "event_types": 1,
                }
            },
        ]
        return await self.collection.aggregate(pipeline).to_list(length=limit)

    async def aggregate_event_type_stats(self) -> list[dict]:
        pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "types": {"$push": {"event_type": "$_id", "count": "$count"}},
                    "total": {"$sum": "$count"},
                }
            },
            {"$unwind": "$types"},
            {
                "$project": {
                    "_id": 0,
                    "event_type": "$types.event_type",
                    "count": "$types.count",
                    "percentage": {
                        "$round": [
                            {
                                "$multiply": [
                                    {"$divide": ["$types.count", "$total"]},
                                    100,
                                ]
                            },
                            2,
                        ]
                    },
                }
            },
            {"$sort": {"count": -1}},
        ]
        return await self.collection.aggregate(pipeline).to_list(length=None)

    async def aggregate_time_series(
        self,
        time_from: datetime,
        time_to: datetime,
        granularity: str = "hour",  # "minute" | "hour" | "day"
    ) -> list[dict]:
        pipeline = [
            {"$match": {"created_at": {"$gte": time_from, "$lte": time_to}}},
            {
                "$group": {
                    "_id": {"$dateTrunc": {"date": "$created_at", "unit": granularity}},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    "timestamp": "$_id",
                    "count": 1,
                }
            },
        ]
        return await self.collection.aggregate(pipeline).to_list(length=None)

    async def aggregate_user_anomalies(
        self,
        time_from: datetime,
        std_threshold: float = 1.0,
    ) -> list[dict]:
        pipeline = [
            {"$match": {"created_at": {"$gte": time_from}, "user_id": {"$ne": None}}},
            # Шаг 1: дневная активность каждого пользователя
            {
                "$group": {
                    "_id": {
                        "user_id": "$user_id",
                        "day": {"$dateTrunc": {"date": "$created_at", "unit": "day"}},
                    },
                    "daily_count": {"$sum": 1},
                }
            },
            # Шаг 2: статистика по пользователю
            {
                "$group": {
                    "_id": "$_id.user_id",
                    "avg_daily": {"$avg": "$daily_count"},
                    "std_daily": {"$stdDevPop": "$daily_count"},
                    "max_daily": {"$max": "$daily_count"},
                    "days_active": {"$sum": 1},
                }
            },
            # Шаг 3: отсеиваем тех, у кого max > avg + threshold * std
            {
                "$addFields": {
                    "threshold": {
                        "$add": [
                            "$avg_daily",
                            {"$multiply": ["$std_daily", std_threshold]},
                        ]
                    },
                }
            },
            {
                "$match": {
                    "$expr": {"$gt": ["$max_daily", "$threshold"]},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "user_id": "$_id",
                    "avg_daily_events": {"$round": ["$avg_daily", 2]},
                    "std_deviation": {"$round": ["$std_daily", 2]},
                    "max_daily_events": "$max_daily",
                    "days_active": 1,
                    "anomaly_score": {
                        "$round": [{"$divide": ["$max_daily", "$threshold"]}, 2]
                    },
                }
            },
            {"$sort": {"anomaly_score": -1}},
        ]
        return await self.collection.aggregate(pipeline).to_list(length=None)
