from datetime import datetime

from pydantic import BaseModel


class RefreshTokenBase(BaseModel):
    user_id: int
    token_hash: str
    expires_at: datetime


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenOut(RefreshTokenBase):
    id: int
    created_at: datetime




