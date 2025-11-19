from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CartBase(BaseModel):
    user_id: int
    total_amount: Decimal


class CartCreate(BaseModel):
    user_id: int
    total_amount: Decimal | None = None


class CartUpdate(BaseModel):
    user_id: int | None = None
    total_amount: Decimal | None = None


class CartOut(CartBase):
    id: int
    created_at: datetime
    username: str | None = None




