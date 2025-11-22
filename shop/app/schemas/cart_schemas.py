from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from shop.app.schemas.cart_item_schemas import CartItemOut


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


class CartWithItems(CartOut):
    items: list[CartItemOut] = Field(default_factory=list)




