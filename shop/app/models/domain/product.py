from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ProductCreateData:
    title: str
    description: str
    price: Decimal
    stock: int
    brand: str
    is_published: bool
    category_id: int
    thumbnail_key: str


@dataclass
class Product:
    id: int
    title: str
    description: str
    price: Decimal
    stock: int
    brand: str
    is_published: bool
    category_id: int
    thumbnail_key: str
