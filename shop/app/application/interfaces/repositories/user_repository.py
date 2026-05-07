from abc import ABC, abstractmethod
from uuid import UUID

from shop.app.domain.entities.user import User


class UserRepository(ABC):
    """Persistence port for user accounts."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Load a user by id."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Load a user by email."""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Load a user by username."""

    @abstractmethod
    async def list_paginated(self, limit: int, offset: int) -> list[User]:
        """Page through users."""

    @abstractmethod
    async def add(self, user: User) -> None:
        """Insert a new user."""

    @abstractmethod
    async def update(self, user: User) -> None:
        """Persist changes to an existing user."""

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Remove a user by id."""

    @abstractmethod
    async def exists_email(self, email: str, *, exclude_id: UUID | None = None) -> bool:
        """Return True if email is registered."""

    @abstractmethod
    async def exists_username(self, username: str, *, exclude_id: UUID | None = None) -> bool:
        """Return True if username is taken."""
