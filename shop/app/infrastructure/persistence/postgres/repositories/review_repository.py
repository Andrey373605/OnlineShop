from uuid import UUID

from shop.app.domain.entities.review import Review
from shop.app.application.interfaces.repositories import ReviewRepository


class ReviewRepositorySql(ReviewRepository):
    def __init__(self, conn):
        self._conn = conn

    async def list_paginated(self, limit: int, offset: int) -> list[Review]:
        rows = await self._conn.fetch(
            """
            SELECT r.id, r.user_id, u.username, r.product_id, p.title AS product_title,
                   r.title, r.description, r.rating, r.created_at, r.updated_at
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN products p ON r.product_id = p.id
            ORDER BY r.id
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset,
        )
        return [self._map_review(row) for row in rows]

    async def get_by_id(self, review_id: UUID) -> Review | None:
        row = await self._conn.fetchrow(
            """
            SELECT r.id, r.user_id, u.username, r.product_id, p.title AS product_title,
                   r.title, r.description, r.rating, r.created_at, r.updated_at
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN products p ON r.product_id = p.id
            WHERE r.id = $1;
            """,
            review_id,
        )
        return self._map_review(row) if row else None

    async def get_by_user_and_product(
        self,
        user_id: UUID,
        product_id: UUID,
    ) -> Review | None:
        row = await self._conn.fetchrow(
            """
            SELECT r.id, r.user_id, u.username, r.product_id, p.title AS product_title,
                   r.title, r.description, r.rating, r.created_at, r.updated_at
            FROM reviews r
            LEFT JOIN users u ON r.user_id = u.id
            LEFT JOIN products p ON r.product_id = p.id
            WHERE r.user_id = $1 AND r.product_id = $2;
            """,
            user_id,
            product_id,
        )
        return self._map_review(row) if row else None

    async def list_by_product(self, product_id: UUID, limit: int, offset: int) -> list[Review]:
        rows = await self._conn.fetch(
            """
            SELECT r.id, r.user_id, r.product_id, r.title, r.description, r.rating, r.created_at, r.updated_at
            FROM reviews r
            WHERE r.product_id = $1
            ORDER BY r.id
            LIMIT $2 OFFSET $3;
            """,
            product_id,
            limit,
            offset,
        )
        return [self._map_review(row) for row in rows]

    async def add(self, review: Review) -> None:
        await self._conn.execute(
            """
            INSERT INTO reviews (user_id, product_id, title, description, rating)
            VALUES ($1, $2, $3, $4, $5);
            """,
            review.user_id,
            review.product_id,
            review.title,
            review.description,
            review.rating,
        )

    async def create(self, data: dict) -> int:
        result = await self._conn.fetchrow(
            """
            INSERT INTO reviews (user_id, product_id, title, description, rating)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id;
            """,
            data.get("user_id"),
            data.get("product_id"),
            data.get("title"),
            data.get("description"),
            data.get("rating"),
        )
        return result["id"]

    async def update(self, review: Review) -> None:
        await self._conn.execute(
            """
            UPDATE reviews
            SET title = $2,
                description = $3,
                rating = $4,
                updated_at = NOW()
            WHERE id = $1
            """,
            review.id,
            review.title,
            review.description,
            review.rating,
        )

    async def delete(self, review_id: UUID) -> None:
        await self._conn.execute(
            "DELETE FROM reviews WHERE id = $1;",
            review_id,
        )

    async def get_all(self, limit: int, offset: int) -> list[Review]:
        return await self.list_paginated(limit, offset)

    @staticmethod
    def _map_review(row) -> Review:
        return Review(
            id=row["id"],
            user_id=row["user_id"],
            product_id=row["product_id"],
            title=row["title"],
            description=row["description"],
            rating=row["rating"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
