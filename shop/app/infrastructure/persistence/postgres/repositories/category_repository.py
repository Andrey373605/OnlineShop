from typing import Any, Mapping
from uuid import UUID

import asyncpg
from asyncpg import Connection

from shop.app.domain import Category
from shop.app.infrastructure.persistence.postgres.repositories.exceptions import (
    RepositoryForeignKeyError,
    RepositoryMappingError,
    RepositoryUnavailableError,
    RepositoryUniqueConstraintError,
)
from shop.app.application.interfaces.repositories import CategoryRepository


class CategoryRepositorySql(CategoryRepository):
    def __init__(self, conn: Connection):
        self._conn: Connection = conn

    async def get_by_id(self, category_id: UUID) -> Category | None:
        try:
            row = await self._conn.fetchrow(
                "SELECT id, name FROM categories WHERE id = $1;",
                category_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch category") from exc

        return self._map_row(row) if row else None

    async def get_by_name(self, name: str) -> Category | None:
        try:
            row = await self._conn.fetchrow(
                "SELECT id, name FROM categories WHERE name = $1;",
                name,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch category by name") from exc
        return self._map_row(row) if row else None

    async def list_all(self) -> list[Category]:
        try:
            rows = await self._conn.fetch("SELECT id, name FROM categories;")
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch categories") from exc
        return [self._map_row(row) for row in rows]

    async def add(self, category: Category) -> None:
        try:
            await self._conn.execute(
                "INSERT INTO categories (name) VALUES ($1);",
                category.name,
            )
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Category name must be unique") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to create category") from exc

    async def update(self, category: Category) -> None:
        try:
            await self._conn.execute(
                "UPDATE categories SET name = $2 WHERE id = $1;",
                category.id,
                category.name,
            )
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Category name must be unique") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to update category") from exc

    async def delete(self, category_id: UUID) -> None:
        try:
            await self._conn.execute(
                "DELETE FROM categories WHERE id = $1;",
                category_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Category is referenced by another entity") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete category") from exc

    async def exists_with_name(self, name: str, *, exclude_id: UUID | None = None) -> bool:
        try:
            if exclude_id is None:
                row = await self._conn.fetchrow(
                    "SELECT EXISTS(SELECT 1 FROM categories WHERE name = $1) AS exists;",
                    name,
                )
            else:
                row = await self._conn.fetchrow(
                    "SELECT EXISTS(SELECT 1 FROM categories WHERE name = $1 AND id <> $2) AS exists;",
                    name,
                    exclude_id,
                )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to check category by name") from exc
        return bool(row["exists"])

    # Backward-compatible aliases for existing SQL services.
    async def get_all(self) -> list[Category]:
        return await self.list_all()

    async def create(self, category_data) -> Category:
        name = category_data.name if hasattr(category_data, "name") else category_data["name"]
        category = Category(id=UUID(int=0), name=name)
        await self.add(category)
        created = await self.get_by_name(name)
        if created is None:
            raise RepositoryUnavailableError("Failed to fetch created category")
        return created

    async def exists_category_with_name(self, category_name: str) -> bool:
        return await self.exists_with_name(category_name)

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> Category:
        try:
            return Category(
                id=row["id"],
                name=row["name"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RepositoryMappingError("Category row has invalid shape") from exc
