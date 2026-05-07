
from typing import cast

from shop.app.domain.errors import EmptySkuError, EmptyStorageKeyError


class Sku(str):
    def __new__(cls, value: str) -> Sku:
        if not isinstance(value, str):
            raise EmptySkuError("SKU must be a string")
        clean = value.strip()
        if not clean:
            raise EmptySkuError("SKU cannot be empty")
        return cast(Sku, str.__new__(cls, clean))


class StorageKey(str):
    def __new__(cls, value: str) -> StorageKey:
        if not isinstance(value, str):
            raise EmptyStorageKeyError("Storage key must be a string")
        clean = value.strip()
        if not clean:
            raise EmptyStorageKeyError("Storage key cannot be empty")
        return cast(StorageKey, str.__new__(cls, clean))


__all__ = ["Sku", "StorageKey"]
