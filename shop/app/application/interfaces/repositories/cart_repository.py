from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.cart import Cart


class CartRepository(ABC):
    """Persistence port for the shopping-cart aggregate (cart + line items)."""

    @abstractmethod
    async def get_by_id(self, cart_id: UUID) -> Cart | None:
        """Load a cart aggregate by id."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Cart | None:
        """Load the cart for a user, if any."""

    @abstractmethod
    async def add(self, cart: Cart) -> None:
        """Insert a new cart and its lines."""

    @abstractmethod
    async def update(self, cart: Cart) -> None:
        """Persist the full cart aggregate state."""

    @abstractmethod
    async def delete(self, cart_id: UUID) -> None:
        """Remove a cart and its lines by cart id."""
