from uuid import UUID

from uuid6 import uuid7

from shop.app.domain.errors import EmptyWarehouseNameError


def _normalize_warehouse_name(name: str) -> str:
    if not isinstance(name, str):
        raise EmptyWarehouseNameError("Warehouse name must be a string")
    clean = name.strip()
    if not clean:
        raise EmptyWarehouseNameError("Warehouse name cannot be empty")
    return clean


class Warehouse:
    def __init__(self, id: UUID, name: str, address: str, is_active: bool = True):
        self._id = id
        self._name = _normalize_warehouse_name(name)
        self._address = address.strip() if address is not None else ""
        self._is_active = is_active

    @classmethod
    def create(cls, name: str, address: str) -> "Warehouse":
        return cls(id=uuid7(), name=name, address=address)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> str:
        return self._address

    @property
    def is_active(self) -> bool:
        return self._is_active

    def deactivate(self) -> None:
        self._is_active = False

    def activate(self) -> None:
        self._is_active = True

    def __repr__(self) -> str:
        return f"<Warehouse {self._name} ({self._id})>"
