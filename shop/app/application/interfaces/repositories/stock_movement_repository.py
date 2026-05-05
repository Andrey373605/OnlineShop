from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from shop.app.domain import StockMovement


class StockMovementRepository(ABC):
    """Append-only persistence port for inventory movements."""

    @abstractmethod
    async def add(self, movement: StockMovement) -> None:
        """Record a new stock movement (immutable log entry)."""

    @abstractmethod
    async def list_by_warehouse(
        self, warehouse_id: UUID, limit: int, offset: int
    ) -> list[StockMovement]:
        """Page movements for one warehouse."""

    @abstractmethod
    async def list_by_product(
        self, product_id: UUID, limit: int, offset: int
    ) -> list[StockMovement]:
        """Page movements affecting a product."""

    @abstractmethod
    async def list_by_variant(
        self, variant_id: UUID, limit: int, offset: int
    ) -> list[StockMovement]:
        """Page movements tied to a variant."""

    @abstractmethod
    async def list_by_period(
        self,
        time_from: datetime,
        time_to: datetime,
        *,
        limit: int,
        offset: int,
    ) -> list[StockMovement]:
        """Page movements within a time window."""
