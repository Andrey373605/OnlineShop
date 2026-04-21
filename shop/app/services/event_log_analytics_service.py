import csv
import io
import json
from datetime import datetime

from shop.app.models.schemas import (
    ActivityByPeriod,
    EventTypeStats,
    TimeSeriesPoint,
    TopUser,
    UserAnomaly,
)
from shop.app.repositories.protocols import EventLogAnalyticsRepository


class EventLogAnalyticsService:
    def __init__(self, repo: EventLogAnalyticsRepository) -> None:
        self._repo = repo

    async def activity_by_period(
        self,
        period: str,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
    ) -> list[ActivityByPeriod]:
        rows = await self._repo.aggregate_activity_by_period(period, time_from, time_to)
        return [ActivityByPeriod(**r) for r in rows]

    async def top_users(self, limit: int = 10) -> list[TopUser]:
        rows = await self._repo.aggregate_top_users(limit)
        return [TopUser(**r) for r in rows]

    async def event_type_stats(self) -> list[EventTypeStats]:
        rows = await self._repo.aggregate_event_type_stats()
        return [EventTypeStats(**r) for r in rows]

    async def time_series(
        self,
        time_from: datetime,
        time_to: datetime,
        granularity: str = "hour",
    ) -> list[TimeSeriesPoint]:
        rows = await self._repo.aggregate_time_series(time_from, time_to, granularity)
        return [TimeSeriesPoint(**r) for r in rows]

    async def user_anomalies(
        self,
        time_from: datetime,
        std_threshold: float = 1.0,
    ) -> list[UserAnomaly]:
        rows = await self._repo.aggregate_user_anomalies(time_from, std_threshold)
        return [UserAnomaly(**r) for r in rows]

    @staticmethod
    def to_json(data: list) -> str:
        return json.dumps(
            [item.model_dump(mode="json") for item in data],
            ensure_ascii=False,
            indent=2,
        )

    @staticmethod
    def to_csv(data: list) -> str:
        if not data:
            return ""
        buf = io.StringIO()
        fields = list(data[0].model_dump().keys())
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        for item in data:
            writer.writerow(item.model_dump(mode="json"))
        return buf.getvalue()
