from shop.app.core.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.models.schemas import OrderCreate, OrderOut, OrderUpdate
from shop.app.repositories.protocols import UnitOfWork


class OrderService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def list_orders(self, limit: int, offset: int) -> list[OrderOut]:
        async with self._uow as uow:
            return await uow.orders.get_all(limit=limit, offset=offset)

    async def get_order_by_id(self, order_id: int) -> OrderOut:
        async with self._uow as uow:
            return await self._get_order_or_raise(uow, order_id)

    async def create_order(self, data: OrderCreate) -> OrderOut:
        async with self._uow as uow:
            if await uow.orders.get_by_number(data.order_number):
                raise AlreadyExistsError("Order number")

            order_id = await uow.orders.create(data.model_dump())
            order = await self._get_order_or_fail(
                uow, order_id, "Unable to fetch created order"
            )
            await uow.commit()
            return order

    async def update_order(self, order_id: int, data: OrderUpdate) -> OrderOut:
        async with self._uow as uow:
            await self._get_order_or_raise(uow, order_id)

            update_data = data.model_dump(exclude_unset=True)
            updated = await uow.orders.update(order_id, update_data)
            if not updated:
                raise OperationFailedError("Failed to update order")

            order = await self._get_order_or_fail(
                uow, order_id, "Unable to fetch updated order"
            )
            await uow.commit()
            return order

    async def delete_order(self, order_id: int) -> None:
        async with self._uow as uow:
            await self._get_order_or_raise(uow, order_id)
            await uow.order_items.delete_by_order_id(order_id)
            deleted = await uow.orders.delete(order_id)
            if not deleted:
                raise OperationFailedError("Failed to delete order")
            await uow.commit()

    @staticmethod
    async def _get_order_or_raise(uow: UnitOfWork, order_id: int) -> OrderOut:
        order = await uow.orders.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order")
        return order

    @staticmethod
    async def _get_order_or_fail(
        uow: UnitOfWork, order_id: int, detail: str
    ) -> OrderOut:
        order = await uow.orders.get_by_id(order_id)
        if not order:
            raise OperationFailedError(detail)
        return order
