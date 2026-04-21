from datetime import datetime

from fastapi import APIRouter, Depends, Query

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_event_log_service
from shop.app.models.schemas import EventLogFilter, EventLogListOut, UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/event-logs", tags=["Event Logs"])


@router.get("", response_model=EventLogListOut)
async def list_event_logs(
    time_from: datetime | None = Query(None, description="Начало интервала (ISO 8601)"),
    time_to: datetime | None = Query(None, description="Конец интервала (ISO 8601)"),
    user_id: int | None = Query(None, description="Фильтр по ID пользователя"),
    event_type: str | None = Query(
        None, description="Тип события (AUTH_LOGIN, HTTP_REQUEST и т.д.)"
    ),
    limit: int = Query(20, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение"),
    current_user: UserOut = Depends(get_current_user),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> EventLogListOut:
    """
    Поиск и фильтрация логов событий по временному интервалу, пользователю и типу события.
    Доступно только администраторам.
    """
    _ensure_admin(current_user)
    filter_params = EventLogFilter(
        time_from=time_from,
        time_to=time_to,
        user_id=user_id,
        event_type=event_type,
    )
    return await event_log_service.list_events(
        limit=limit,
        offset=offset,
        filter_params=filter_params,
    )
