import logging
from typing import Any

from fastapi import Request

from shop.app.repositories.event_log_repository import EventLogRepository
from shop.app.schemas.event_log_schemas import EventLogCreate, EventLogOut


class EventLogService:
    def __init__(self, repo: EventLogRepository) -> None:
        self.repo = repo
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
        )

        try:
            return await self.repo.create(payload.model_dump())
        except Exception as exc:  # pragma: no cover - logging best-effort
            self._logger.exception("Failed to persist event log: %s", exc)
            return None

    async def list_events(self, limit: int, offset: int) -> list[EventLogOut]:
        return await self.repo.get_all(limit=limit, offset=offset)

    async def get_event(self, event_id: int) -> EventLogOut | None:
        return await self.repo.get_by_id(event_id)


