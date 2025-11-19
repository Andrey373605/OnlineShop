from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderBase(BaseModel):
    user_id: int
    order_number: str
    status: str
    total_amount: Decimal
    shipping_address: str
    payment_method: str
    payment_status: str


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: str | None = None
    total_amount: Decimal | None = None
    shipping_address: str | None = None
    payment_method: str | None = None
    payment_status: str | None = None


class OrderOut(OrderBase):
    id: int
    created_at: datetime
    username: str | None = None




