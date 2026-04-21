import logging

from fastapi import Request

from shop.app.models.schemas import (
    EventLogCreate,
    EventLogFilter,
    EventLogListOut,
    EventLogOut,
    EventType,
)
from shop.app.repositories.protocols import EventLogRepository


class EventLogService:
    def __init__(self, repo: EventLogRepository) -> None:
        self._repo = repo
        self._logger = logging.getLogger(__name__)

    async def log_event(
        self,
        event_type: str,
        *,
        user_id: int | None = None,
        description: str | None = None,
        request: Request | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        error_message: str | None = None,
        stack_trace: str | None = None,
        detail: dict | None = None,
    ) -> int | None:
        if request is not None:
            if request.client:
                ip_address = ip_address or request.client.host
            user_agent = user_agent or request.headers.get("user-agent")

        payload = EventLogCreate(
            event_type=event_type,
            user_id=user_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
            stack_trace=stack_trace,
            detail=detail,
        )

        try:
            return await self._repo.create(payload.model_dump(exclude_none=True))
        except Exception as exc:  # pragma: no cover - logging best-effort
            self._logger.exception("Failed to persist event log: %s", exc)
            return None

    async def log_error(
        self,
        description: str,
        *,
        request: Request | None = None,
        error_message: str | None = None,
        stack_trace: str | None = None,
        user_id: int | None = None,
    ) -> int | None:
        """Логирование ошибок и исключений приложения в MongoDB."""
        return await self.log_event(
            EventType.APP_ERROR,
            description=description,
            request=request,
            error_message=error_message or description,
            stack_trace=stack_trace,
            user_id=user_id,
        )

    async def log_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        *,
        request: Request | None = None,
        db_used: bool = False,
        user_id: int | None = None,
    ) -> int | None:
        """Логирование HTTP-запроса и факта обращения к реляционной БД."""
        return await self.log_event(
            EventType.HTTP_REQUEST,
            description=f"{method} {path} -> {status_code}",
            request=request,
            user_id=user_id,
            detail={
                "method": method,
                "path": path,
                "status_code": status_code,
                "db_used": db_used,
            },
        )

    async def list_events(
        self,
        limit: int,
        offset: int,
        filter_params: EventLogFilter | None = None,
    ) -> EventLogListOut:
        """Список логов с опциональной фильтрацией по времени, пользователю и типу события."""
        time_from = time_to = user_id = event_type = None
        if filter_params is not None:
            time_from = filter_params.time_from
            time_to = filter_params.time_to
            user_id = filter_params.user_id
            event_type = filter_params.event_type
        items, total = await self._repo.get_filtered(
            time_from=time_from,
            time_to=time_to,
            user_id=user_id,
            event_type=event_type,
            limit=limit,
            offset=offset,
        )
        return EventLogListOut(items=items, total=total)

    async def get_event(self, event_id: int) -> EventLogOut | None:
        return await self._repo.get_by_id(event_id)
