from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.order import Order


class OrderRepository(ABC):
    """Persistence port for the order aggregate (header + line items)."""

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        """Load an order aggregate by id."""

    @abstractmethod
    async def get_by_order_number(self, order_number: str) -> Order | None:
        """Resolve an order by business order number."""

    @abstractmethod
    async def list_for_user(self, user_id: UUID, limit: int, offset: int) -> list[Order]:
        """Page orders placed by a user."""

    @abstractmethod
    async def list_paginated(self, limit: int, offset: int) -> list[Order]:
        """Page all orders (e.g. admin)."""

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Insert a new order and its lines."""

    @abstractmethod
    async def update(self, order: Order) -> None:
        """Persist changes to an existing order aggregate."""

    @abstractmethod
    async def delete(self, order_id: UUID) -> None:
        """Remove an order by id (policy-dependent; port allows hard delete)."""
