from copy import deepcopy
from typing import Any
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.attributes import coerce_attributes_dict


class ProductDetails:
    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self._id = id
        self._product_id = product_id
        self._attributes = coerce_attributes_dict(attributes)

    @classmethod
    def create(
        cls,
        product_id: UUID,
        attributes: dict[str, Any] | None = None,
    ) -> "ProductDetails":
        return cls(id=uuid7(), product_id=product_id, attributes=attributes)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def product_id(self) -> UUID:
        return self._product_id

    @property
    def attributes(self) -> dict[str, Any]:
        return deepcopy(self._attributes)

    def replace_attributes(self, attributes: dict[str, Any] | None) -> None:
        self._attributes = coerce_attributes_dict(attributes)

    def __repr__(self) -> str:
        return f"<ProductDetails product={self._product_id} ({self._id})>"
