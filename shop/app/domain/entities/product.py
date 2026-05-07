from decimal import Decimal

from uuid import UUID

from shop.app.domain.errors import DomainValidationError, EmptyProductTitleError


class Product:
    """Catalog product as mapped from current SQL schema."""

    def __init__(
        self,
        id: UUID,
        title: str,
        description: str,
        price: Decimal,
        stock: int,
        brand: str,
        is_published: bool,
        category_id: UUID,
        thumbnail_key: str,
    ) -> None:
        if not isinstance(id, UUID):
            raise DomainValidationError("Product id must be UUID")
        if not isinstance(title, str):
            raise DomainValidationError("Product title must be a string")
        clean_title = title.strip()
        if not clean_title:
            raise EmptyProductTitleError("Product title cannot be empty")
        if not isinstance(description, str):
            raise DomainValidationError("Product description must be a string")
        if not isinstance(price, Decimal):
            raise DomainValidationError("Product price must be Decimal")
        if price < 0:
            raise DomainValidationError("Product price cannot be negative")
        if not isinstance(stock, int) or isinstance(stock, bool):
            raise DomainValidationError("Product stock must be an integer")
        if stock < 0:
            raise DomainValidationError("Product stock cannot be negative")
        if not isinstance(brand, str) or not brand.strip():
            raise DomainValidationError("Product brand cannot be empty")
        if not isinstance(category_id, UUID):
            raise DomainValidationError("Product category id must be UUID")
        if not isinstance(is_published, bool):
            raise DomainValidationError("Product publish flag must be boolean")
        if not isinstance(thumbnail_key, str) or not thumbnail_key.strip():
            raise DomainValidationError("Product thumbnail key cannot be empty")

        self._id = id
        self._title = clean_title
        self._description = description.strip()
        self._price = price
        self._stock = stock
        self._brand = brand.strip()
        self._is_published = is_published
        self._category_id = category_id
        self._thumbnail_key = thumbnail_key.strip()

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def price(self) -> Decimal:
        return self._price

    @property
    def stock(self) -> int:
        return self._stock

    @property
    def brand(self) -> str:
        return self._brand

    @property
    def is_published(self) -> bool:
        return self._is_published

    @property
    def category_id(self) -> UUID:
        return self._category_id

    @property
    def thumbnail_key(self) -> str:
        return self._thumbnail_key

    def __repr__(self) -> str:
        return f"<Product {self._title!r} ({self._id})>"
