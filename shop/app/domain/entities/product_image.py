from datetime import datetime, UTC
from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.value_objects.catalog_values import StorageKey


class ProductImage:
    def __init__(
        self,
        id: UUID,
        product_id: UUID,
        storage_key: StorageKey,
        created_at: datetime | None = None,
    ):
        self._id = id
        self._product_id = product_id
        self._storage_key = storage_key
        self._created_at = created_at or datetime.now(UTC)

    @classmethod
    def create(cls, product_id: UUID, storage_key: StorageKey) -> "ProductImage":
        return cls(id=uuid7(), product_id=product_id, storage_key=storage_key)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def product_id(self) -> UUID:
        return self._product_id

    @property
    def storage_key(self) -> StorageKey:
        return self._storage_key

    def generate_public_url(self, base_url: str) -> str:
        return f"{base_url.rstrip('/')}/{self._storage_key}"

    def rename_storage_key(self, new_key: StorageKey) -> None:
        self._storage_key = new_key

    def __repr__(self) -> str:
        return f"<ProductImage(id={self._id}, product={self._product_id})>"
