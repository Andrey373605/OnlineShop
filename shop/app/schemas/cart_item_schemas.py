from decimal import Decimal

from pydantic import BaseModel, conint


class CartItemBase(BaseModel):
    cart_id: int
    product_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    cart_id: int | None = None
    product_id: int | None = None
    quantity: int | None = None


class CartItemOut(CartItemBase):
    id: int
    product_title: str | None = None
    product_price: Decimal | None = None
    line_total: Decimal | None = None


class CartItemAdd(BaseModel):
    product_id: int
    quantity: conint(gt=0) = 1


class CartItemQuantityUpdate(BaseModel):
    quantity: conint(gt=0)



