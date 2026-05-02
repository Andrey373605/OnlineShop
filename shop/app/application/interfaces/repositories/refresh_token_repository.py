from abc import ABC, abstractmethod

from shop.app.models.schemas import RefreshTokenOut


class RefreshTokenRepository(ABC):
    """Technical persistence port for refresh-token rows (no domain model yet)."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[RefreshTokenOut]:
        """List refresh tokens issued to a user (newest first)."""

    @abstractmethod
    async def get_by_hash(self, token_hash: str) -> RefreshTokenOut | None:
        """Look up a token row by its hashed value."""

    @abstractmethod
    async def create(self, data: dict) -> int:
        """Store a new refresh token; return id."""

    @abstractmethod
    async def delete(self, token_id: int) -> bool:
        """Delete a token by primary key; return True if removed."""

    @abstractmethod
    async def delete_by_hash(self, token_hash: str) -> list[int]:
        """Revoke every row matching the hash; return deleted ids."""

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> list[int]:
        """Revoke all tokens for a user; return deleted ids."""
