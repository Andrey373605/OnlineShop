from typing import Any, Mapping

import asyncpg
from asyncpg import Connection
from shop.app.models.domain.category import Category, CategoryCreateData, CategoryUpdateData
from shop.app.repositories.exceptions import (
    RepositoryForeignKeyError,
    RepositoryMappingError,
    RepositoryRecordNotFoundError,
    RepositoryUnavailableError,
    RepositoryUnexpectedResultError,
    RepositoryUniqueConstraintError,
)
from shop.app.repositories.protocols import CategoryRepository


class CategoryRepositorySql(CategoryRepository):
    def __init__(self, conn: Connection):
        self._conn: Connection = conn

    async def get_by_id(self, category_id: int) -> Category:
        try:
            row = await self._conn.fetchrow(
                "SELECT id, name FROM categories WHERE id = $1;",
                category_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch category") from exc

        if not row:
            raise RepositoryRecordNotFoundError("Category not found")

        return self._map_row(row)

    async def get_all(self) -> list[Category]:
        try:
            rows = await self._conn.fetch("SELECT id, name FROM categories;")
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to fetch categories") from exc
        return [self._map_row(row) for row in rows]

    async def create(self, category_data: CategoryCreateData) -> Category:
        try:
            row = await self._conn.fetchrow(
                "INSERT INTO categories (name) VALUES ($1) RETURNING id, name;",
                category_data.name,
            )
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Category name must be unique") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to create category") from exc

        if not row:
            raise RepositoryUnexpectedResultError("Database did not return created category")
        return self._map_row(row)

    async def update(self, category_id: int, update_data: CategoryUpdateData) -> Category:
        try:
            row = await self._conn.fetchrow(
                """
                UPDATE categories
                SET name = COALESCE($2, name)
                WHERE id = $1
                RETURNING id, name;
                """,
                category_id,
                update_data.name,
            )
        except asyncpg.UniqueViolationError as exc:
            raise RepositoryUniqueConstraintError("Category name must be unique") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to update category") from exc

        if not row:
            raise RepositoryRecordNotFoundError("Category not found")

        return self._map_row(row)

    async def delete(self, category_id: int) -> Category:
        try:
            row = await self._conn.fetchrow(
                "DELETE FROM categories WHERE id = $1 RETURNING id, name;",
                category_id,
            )
        except asyncpg.ForeignKeyViolationError as exc:
            raise RepositoryForeignKeyError("Category is referenced by another entity") from exc
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to delete category") from exc

        if not row:
            raise RepositoryRecordNotFoundError("Category not found")
        return self._map_row(row)

    async def exists_category_with_id(self, category_id: int) -> bool:
        try:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM categories WHERE id = $1) AS exists;",
                category_id,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to check category by id") from exc
        return row["exists"]

    async def exists_category_with_name(self, category_name: str) -> bool:
        try:
            row = await self._conn.fetchrow(
                "SELECT EXISTS(SELECT 1 FROM categories WHERE name = $1) AS exists;",
                category_name,
            )
        except asyncpg.PostgresError as exc:
            raise RepositoryUnavailableError("Failed to check category by name") from exc
        return row["exists"]

    @staticmethod
    def _map_row(row: Mapping[str, Any]) -> Category:
        try:
            return Category(
                id=row["id"],
                name=row["name"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise RepositoryMappingError("Category row has invalid shape") from exc
