from shop.app.models.schemas import ReviewOut
from shop.app.repositories.protocols import ReviewRepository


class ReviewRepositorySql(ReviewRepository):
    def __init__(self, conn):
        self._conn = conn

    async def get_all(self, limit: int, offset: int) -> list[ReviewOut]:
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
        return [ReviewOut(**row) for row in rows]

    async def get_by_id(self, review_id: int) -> ReviewOut | None:
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
        return ReviewOut(**row) if row else None

    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int,
    ) -> ReviewOut | None:
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
        return ReviewOut(**row) if row else None

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

    async def update(self, review_id: int, data: dict) -> bool:
        result = await self._conn.fetchrow(
            """
            UPDATE reviews
            SET title = COALESCE($2, title),
                description = COALESCE($3, description),
                rating = COALESCE($4, rating),
                updated_at = NOW()
            WHERE id = $1
            RETURNING id, user_id, product_id, rating;
            """,
            review_id,
            data.get("title"),
            data.get("description"),
            data.get("rating"),
        )
        return bool(result)

    async def delete(self, review_id: int) -> bool:
        result = await self._conn.fetchrow(
            "DELETE FROM reviews WHERE id = $1 RETURNING id;",
            review_id,
        )
        return bool(result)
