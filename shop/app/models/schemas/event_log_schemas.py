from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# Типы событий для единообразия
class EventType(Enum):
    AUTH_LOGIN = "AUTH_LOGIN"
    AUTH_LOGOUT = "AUTH_LOGOUT"
    AUTH_REGISTER = "AUTH_REGISTER"
    AUTH_REFRESH = "AUTH_REFRESH"
    OBJECT_CREATE = "OBJECT_CREATE"
    OBJECT_UPDATE = "OBJECT_UPDATE"
    OBJECT_DELETE = "OBJECT_DELETE"
    HTTP_REQUEST = "HTTP_REQUEST"
    DB_ACCESS = "DB_ACCESS"
    APP_ERROR = "APP_ERROR"


class EventLogBase(BaseModel):
    event_type: str
    user_id: int | None = None
    description: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    detail: dict | None = None


class EventLogCreate(EventLogBase):
    pass


class EventLogOut(EventLogBase):
    id: int
    created_at: datetime


class EventLogFilter(BaseModel):
    """Параметры поиска и фильтрации логов событий."""

    time_from: datetime | None = Field(None, description="Начало временного интервала (включительно)")
    time_to: datetime | None = Field(None, description="Конец временного интервала (включительно)")
    user_id: int | None = Field(None, description="Фильтр по ID пользователя")
    event_type: str | None = Field(None, description="Тип события (например AUTH_LOGIN, HTTP_REQUEST)")


class EventLogListOut(BaseModel):
    """Список логов с общим количеством для пагинации."""

    items: list[EventLogOut]
    total: int



