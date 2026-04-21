import enum
from datetime import datetime

from pydantic import BaseModel, Field


class PeriodEnum(enum.StrEnum):
    day = "day"
    week = "week"
    month = "month"


class StatsOut(BaseModel):
    total_orders: int
    total_users: int
    total_products: int


class ActivityByPeriod(BaseModel):
    period: datetime
    event_count: int
    unique_users: int


class TopUser(BaseModel):
    user_id: int
    event_count: int
    last_activity: datetime
    event_types: list[str]


class EventTypeStats(BaseModel):
    event_type: str
    count: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    count: int


class UserAnomaly(BaseModel):
    user_id: int
    avg_daily_events: float
    std_deviation: float
    max_daily_events: int
    days_active: int
    anomaly_score: float = Field(description="Отношение max к (avg + 2*std); >1 = аномалия")
