from fastapi import HTTPException, status

from shop.app.repositories.order_item_repository import OrderItemRepository
from shop.app.repositories.order_repository import OrderRepository
from shop.app.schemas.order_schemas import OrderCreate, OrderOut, OrderUpdate


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        order_item_repo: OrderItemRepository,
    ):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo

    async def list_orders(self, limit: int, offset: int) -> list[OrderOut]:
        return await self.order_repo.get_all(limit=limit, offset=offset)

    async def get_order_by_id(self, order_id: int) -> OrderOut:
        return await self._get_order_or_404(order_id)

    async def create_order(self, data: OrderCreate) -> OrderOut:
        if await self.order_repo.get_by_number(data.order_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order number already exists",
            )

        order_id = await self.order_repo.create(data.model_dump())
        return await self._get_order_or_500(order_id, detail="Unable to fetch created order")

    async def update_order(self, order_id: int, data: OrderUpdate) -> OrderOut:
        await self._get_order_or_404(order_id)

        update_data = data.model_dump(exclude_unset=True)
        updated = await self.order_repo.update(order_id, update_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order",
            )

        return await self._get_order_or_500(order_id, detail="Unable to fetch updated order")

    async def delete_order(self, order_id: int) -> None:
        await self._get_order_or_404(order_id)

        await self.order_item_repo.delete_by_order_id(order_id)
        deleted = await self.order_repo.delete(order_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete order",
            )

    async def _get_order_or_404(self, order_id: int) -> OrderOut:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return order

    async def _get_order_or_500(self, order_id: int, detail: str) -> OrderOut:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail,
            )
        return order



