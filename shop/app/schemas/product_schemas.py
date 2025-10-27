from pydantic import BaseModel, AnyUrl
from decimal import Decimal


class ProductBase(BaseModel):
    title: str
    description: str
    price: Decimal
    stock: int
    brand: str
    thumbnail_url: str
    is_published: bool
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int


class ProductResponse(BaseModel):
    id: int
    message: str
