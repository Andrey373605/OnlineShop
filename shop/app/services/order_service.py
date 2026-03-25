from shop.app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.repositories.protocols import OrderItemRepository, OrderRepository
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
        return await self._get_order_or_raise(order_id)

    async def create_order(self, data: OrderCreate) -> OrderOut:
        if await self.order_repo.get_by_number(data.order_number):
            raise AlreadyExistsError("Order number")

        order_id = await self.order_repo.create(data.model_dump())
        return await self._get_order_or_fail(order_id, detail="Unable to fetch created order")

    async def update_order(self, order_id: int, data: OrderUpdate) -> OrderOut:
        await self._get_order_or_raise(order_id)

        update_data = data.model_dump(exclude_unset=True)
        updated = await self.order_repo.update(order_id, update_data)
        if not updated:
            raise OperationFailedError("Failed to update order")

        return await self._get_order_or_fail(order_id, detail="Unable to fetch updated order")

    async def delete_order(self, order_id: int) -> None:
        await self._get_order_or_raise(order_id)

        await self.order_item_repo.delete_by_order_id(order_id)
        deleted = await self.order_repo.delete(order_id)
        if not deleted:
            raise OperationFailedError("Failed to delete order")

    async def _get_order_or_raise(self, order_id: int) -> OrderOut:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order")
        return order

    async def _get_order_or_fail(self, order_id: int, detail: str) -> OrderOut:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise OperationFailedError(detail)
        return order
