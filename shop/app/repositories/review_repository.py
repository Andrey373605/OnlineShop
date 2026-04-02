from shop.app.models.schemas import ReviewOut


class ReviewRepositorySql:
    def __init__(self, conn, queries):
        self._conn = conn
        self._queries = queries

    async def get_all(self, limit: int, offset: int) -> list[ReviewOut]:
        rows = await self._queries.get_all_reviews(
            self._conn,
            limit=limit,
            offset=offset,
        )
        return [ReviewOut(**row) for row in rows]

    async def get_by_id(self, review_id: int) -> ReviewOut | None:
        row = await self._queries.get_review_by_id(self._conn, id=review_id)
        return ReviewOut(**row) if row else None

    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int,
    ) -> ReviewOut | None:
        row = await self._queries.get_review_by_user_and_product(
            self._conn,
            user_id=user_id,
            product_id=product_id,
        )
        return ReviewOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self._queries.create_review(self._conn, **data)
        return result["id"]

    async def update(self, review_id: int, data: dict) -> bool:
        result = await self._queries.update_review(
            self._conn,
            id=review_id,
            **data,
        )
        return bool(result)

    async def delete(self, review_id: int) -> bool:
        result = await self._queries.delete_review(self._conn, id=review_id)
        return bool(result)
