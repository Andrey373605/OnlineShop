from datetime import datetime

from pydantic import BaseModel


class EventLogBase(BaseModel):
    event_type: str
    user_id: int | None = None
    description: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class EventLogCreate(EventLogBase):
    pass


class EventLogOut(EventLogBase):
    id: int
    created_at: datetime







