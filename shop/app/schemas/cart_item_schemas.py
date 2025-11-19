from pydantic import BaseModel


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



