from datetime import datetime

from pydantic import BaseModel


class SessionInfo(BaseModel):
    session_id: str
    user_id: int
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    instance_id: str

    @classmethod
    def from_redis(cls, data: dict) -> "SessionInfo":
        return cls(
            session_id=data["session_id"],
            user_id=int(data["user_id"]),
            ip_address=data.get("ip_address", ""),
            user_agent=data.get("user_agent", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            instance_id=data.get("instance_id", ""),
        )


class SessionListResponse(BaseModel):
    sessions: list[SessionInfo]
    total: int
