from decimal import Decimal

from pydantic import BaseModel


class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    order_id: int | None = None
    product_id: int | None = None
    quantity: int | None = None
    unit_price: Decimal | None = None


class OrderItemOut(OrderItemBase):
    id: int
    product_title: str | None = None




