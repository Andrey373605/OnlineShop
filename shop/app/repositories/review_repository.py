from shop.app.schemas.review_schemas import ReviewOut


class ReviewRepository:
    def __init__(self, conn, queries):
        self.conn = conn
        self.queries = queries

    async def get_all(self, limit: int, offset: int) -> list[ReviewOut]:
        rows = await self.queries.get_all_reviews(
            self.conn,
            limit=limit,
            offset=offset,
        )
        return [ReviewOut(**row) for row in rows]

    async def get_by_id(self, review_id: int) -> ReviewOut | None:
        row = await self.queries.get_review_by_id(self.conn, id=review_id)
        return ReviewOut(**row) if row else None

    async def get_by_user_and_product(
        self,
        user_id: int,
        product_id: int,
    ) -> ReviewOut | None:
        row = await self.queries.get_review_by_user_and_product(
            self.conn,
            user_id=user_id,
            product_id=product_id,
        )
        return ReviewOut(**row) if row else None

    async def create(self, data: dict) -> int:
        result = await self.queries.create_review(self.conn, **data)
        return result["id"]

    async def update(self, review_id: int, data: dict) -> bool:
        result = await self.queries.update_review(
            self.conn,
            id=review_id,
            **data,
        )
        return bool(result)

    async def delete(self, review_id: int) -> bool:
        result = await self.queries.delete_review(self.conn, id=review_id)
        return bool(result)


