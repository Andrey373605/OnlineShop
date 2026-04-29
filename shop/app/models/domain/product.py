from dataclasses import dataclass
from decimal import Decimal

from shop.app.models.schemas import ProductCreate


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

    @classmethod
    def from_input(cls, data: ProductCreate, thumbnail_key: str) -> "ProductCreateData":
        return cls(
            title=data.title,
            description=data.description,
            price=data.price,
            stock=data.stock,
            brand=data.brand,
            is_published=data.is_published,
            category_id=data.category_id,
            thumbnail_key=thumbnail_key,
        )


@dataclass
class ProductUpdateData:
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    brand: str | None = None
    is_published: bool | None = None
    category_id: int | None = None
    thumbnail_key: str | None = None


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
