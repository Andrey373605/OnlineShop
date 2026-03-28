from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_event_log_analytics_service
from shop.app.schemas.analytics_schemas import (
    ActivityByPeriod,
    EventTypeStats,
    PeriodEnum,
    TimeSeriesPoint,
    TopUser,
    UserAnomaly,
)
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_analytics_service import EventLogAnalyticsService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class ExportFormat(str, Enum):
    json = "json"
    csv = "csv"


@router.get("/activity", response_model=list[ActivityByPeriod])
async def get_activity_by_period(
    period: PeriodEnum = Query(PeriodEnum.day),
    time_from: datetime | None = Query(None),
    time_to: datetime | None = Query(None),
    current_user: UserOut = Depends(get_current_user),
    svc: EventLogAnalyticsService = Depends(get_event_log_analytics_service),
):
    _ensure_admin(current_user)
    return await svc.activity_by_period(period.value, time_from, time_to)


@router.get("/top-users", response_model=list[TopUser])
async def get_top_users(
    limit: int = Query(10, ge=1, le=100),
    current_user: UserOut = Depends(get_current_user),
    svc: EventLogAnalyticsService = Depends(get_event_log_analytics_service),
):
    _ensure_admin(current_user)
    return await svc.top_users(limit)


@router.get("/event-types", response_model=list[EventTypeStats])
async def get_event_type_stats(
    current_user: UserOut = Depends(get_current_user),
    svc: EventLogAnalyticsService = Depends(get_event_log_analytics_service),
):
    _ensure_admin(current_user)
    return await svc.event_type_stats()


@router.get("/time-series", response_model=list[TimeSeriesPoint])
async def get_time_series(
    time_from: datetime = Query(...),
    time_to: datetime = Query(...),
    granularity: str = Query("hour", regex="^(minute|hour|day)$"),
    current_user: UserOut = Depends(get_current_user),
    svc: EventLogAnalyticsService = Depends(get_event_log_analytics_service),
):
    _ensure_admin(current_user)
    return await svc.time_series(time_from, time_to, granularity)


@router.get("/anomalies", response_model=list[UserAnomaly])
async def get_anomalies(
    time_from: datetime = Query(...),
    std_threshold: float = Query(2.0, ge=1.0, le=5.0),
    current_user: UserOut = Depends(get_current_user),
    svc: EventLogAnalyticsService = Depends(get_event_log_analytics_service),
):
    _ensure_admin(current_user)
    return await svc.user_anomalies(time_from, std_threshold)


@router.get("/export/{report_name}")
async def export_report(
    report_name: str,
    fmt: ExportFormat = Query(ExportFormat.json),
    period: PeriodEnum = Query(PeriodEnum.day),
    time_from: datetime | None = Query(None),
    time_to: datetime | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
    current_user: UserOut = Depends(get_current_user),
    svc: EventLogAnalyticsService = Depends(get_event_log_analytics_service),
):
    _ensure_admin(current_user)

    fetchers = {
        "activity": lambda: svc.activity_by_period(period.value, time_from, time_to),
        "top-users": lambda: svc.top_users(limit),
        "event-types": lambda: svc.event_type_stats(),
        "anomalies": lambda: svc.user_anomalies(
            time_from or datetime(2020, 1, 1),
        ),
    }

    fetcher = fetchers.get(report_name)
    if fetcher is None:
        from fastapi import HTTPException

        raise HTTPException(404, f"Unknown report: {report_name}")

    data = await fetcher()

    if fmt == ExportFormat.csv:
        content = svc.to_csv(data)
        return StreamingResponse(
            iter([content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_name}.csv"},
        )

    content = svc.to_json(data)
    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={report_name}.json"},
    )
