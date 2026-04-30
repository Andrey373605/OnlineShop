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
            return await uow.orders.get_by_id(order_id)

    async def create_order(self, data: OrderCreate) -> OrderOut:
        async with self._uow as uow:
            order = await uow.orders.create(data.model_dump())
            await uow.commit()
            return order

    async def update_order(self, order_id: int, data: OrderUpdate) -> OrderOut:
        async with self._uow as uow:
            update_data = data.model_dump(exclude_unset=True)
            order = await uow.orders.update(order_id, update_data)

            await uow.commit()
            return order

    async def delete_order(self, order_id: int) -> None:
        async with self._uow as uow:
            await uow.order_items.delete_by_order_id(order_id)
            await uow.orders.delete(order_id)
            await uow.commit()
