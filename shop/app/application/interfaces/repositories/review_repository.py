from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.review import Review


class ReviewRepository(ABC):
    """Persistence port for product reviews."""

    @abstractmethod
    async def get_by_id(self, review_id: UUID) -> Review | None:
        """Load a review by id."""

    @abstractmethod
    async def get_by_user_and_product(self, user_id: UUID, product_id: UUID) -> Review | None:
        """Return a user's review for a product, if it exists."""

    @abstractmethod
    async def list_by_product(self, product_id: UUID, limit: int, offset: int) -> list[Review]:
        """Page reviews for one product."""

    @abstractmethod
    async def list_paginated(self, limit: int, offset: int) -> list[Review]:
        """Page all reviews (moderation / admin)."""

    @abstractmethod
    async def add(self, review: Review) -> None:
        """Insert a review."""

    @abstractmethod
    async def update(self, review: Review) -> None:
        """Persist changes to a review."""

    @abstractmethod
    async def delete(self, review_id: UUID) -> None:
        """Remove a review by id."""
