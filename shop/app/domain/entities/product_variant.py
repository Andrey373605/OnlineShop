from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.value_objects.catalog_values import Sku
from shop.app.domain.value_objects.price import Price


class ProductVariant:
    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        sku: Sku,
        price: Price,
        display_name: str | None = None,
    ) -> None:
        self._id = id
        self._product_id = product_id
        self._sku = sku
        self._price = price
        self._display_name = display_name.strip() if display_name and display_name.strip() else None

    @classmethod
    def create(
        cls,
        product_id: UUID,
        sku: Sku,
        price: Price,
        display_name: str | None = None,
    ) -> "ProductVariant":
        return cls(
            id=uuid7(),
            product_id=product_id,
            sku=sku,
            price=price,
            display_name=display_name,
        )

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def product_id(self) -> UUID:
        return self._product_id

    @property
    def sku(self) -> Sku:
        return self._sku

    @property
    def price(self) -> Price:
        return self._price

    @property
    def display_name(self) -> str | None:
        return self._display_name

    def change_sku(self, new_sku: Sku) -> None:
        self._sku = new_sku

    def change_price(self, new_price: Price) -> None:
        self._price = new_price

    def change_display_name(self, value: str | None) -> None:
        self._display_name = value.strip() if value and value.strip() else None

    def __repr__(self) -> str:
        return f"<ProductVariant sku={self._sku!r} product={self._product_id} ({self._id})>"
