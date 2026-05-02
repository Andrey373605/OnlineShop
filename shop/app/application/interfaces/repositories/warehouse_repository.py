from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.warehouse import Warehouse


class WarehouseRepository(ABC):
    """Persistence port for stock locations."""

    @abstractmethod
    async def get_by_id(self, warehouse_id: UUID) -> Warehouse | None:
        """Load a warehouse by id."""

    @abstractmethod
    async def list_all(self) -> list[Warehouse]:
        """Return all warehouses."""

    @abstractmethod
    async def add(self, warehouse: Warehouse) -> None:
        """Insert a warehouse."""

    @abstractmethod
    async def update(self, warehouse: Warehouse) -> None:
        """Persist changes to a warehouse."""

    @abstractmethod
    async def delete(self, warehouse_id: UUID) -> None:
        """Remove a warehouse by id."""
