from shop.app.core.exceptions import (
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
)
from shop.app.repositories.protocols import UnitOfWork
from shop.app.schemas.order_item_schemas import (
    OrderItemCreate,
    OrderItemOut,
    OrderItemUpdate,
)


class OrderItemService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def list_order_items(self, order_id: int) -> list[OrderItemOut]:
        async with self.uow as uow:
            await self._get_order_or_raise(uow, order_id)
            return await uow.order_items.get_by_order_id(order_id)

    async def get_order_item(self, order_id: int, item_id: int) -> OrderItemOut:
        async with self.uow as uow:
            item = await self._get_item_or_raise(uow, item_id)
            if item.order_id != order_id:
                raise NotFoundError("Order item")
            return item

    async def create_order_item(
            self,
            order_id: int,
            data: OrderItemCreate,
    ) -> OrderItemOut:
        async with self.uow as uow:
            self._validate_order_item_request(order_id, data.order_id)
            await self._get_order_or_raise(uow, order_id)
            await self._ensure_product_exists(uow, data.product_id)

            payload = data.model_dump()
            payload["order_id"] = order_id

            item_id = await uow.order_items.create(payload)
            item = await self._get_item_or_fail(uow, item_id, "Unable to fetch created order item")
            await uow.commit()
            return item

    async def update_order_item(
            self,
            order_id: int,
            item_id: int,
            data: OrderItemUpdate,
    ) -> OrderItemOut:
        async with self.uow as uow:
            item = await self._get_item_or_raise(uow, item_id)
            if item.order_id != order_id:
                raise NotFoundError("Order item")

            if data.order_id is not None and data.order_id != order_id:
                raise DomainValidationError("Cannot move order item to another order")

            if data.product_id is not None and data.product_id != item.product_id:
                await self._ensure_product_exists(uow, data.product_id)

            update_payload = data.model_dump(exclude_unset=True)
            update_payload["order_id"] = order_id

            updated = await uow.order_items.update(item_id, update_payload)
            if not updated:
                raise OperationFailedError("Failed to update order item")

            item = await self._get_item_or_fail(uow, item_id, "Unable to fetch updated order item")
            await uow.commit()
            return item

    async def delete_order_item(self, order_id: int, item_id: int) -> None:
        async with self.uow as uow:
            item = await self._get_item_or_raise(uow, item_id)
            if item.order_id != order_id:
                raise NotFoundError("Order item")

            deleted = await uow.order_items.delete(item_id)
            if not deleted:
                raise OperationFailedError("Failed to delete order item")
            await uow.commit()

    @staticmethod
    async def _get_order_or_raise(uow: UnitOfWork, order_id: int):
        order = await uow.orders.get_by_id(order_id)
        if not order:
            raise NotFoundError("Order")
        return order

    @staticmethod
    async def _ensure_product_exists(uow: UnitOfWork, product_id: int):
        product = await uow.products.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product")

    @staticmethod
    async def _get_item_or_raise(uow: UnitOfWork, item_id: int) -> OrderItemOut:
        item = await uow.order_items.get_by_id(item_id)
        if not item:
            raise NotFoundError("Order item")
        return item

    @staticmethod
    async def _get_item_or_fail(uow: UnitOfWork, item_id: int, detail: str) -> OrderItemOut:
        item = await uow.order_items.get_by_id(item_id)
        if not item:
            raise OperationFailedError(detail)
        return item

    @staticmethod
    def _validate_order_item_request(
            path_order_id: int,
            body_order_id: int | None,
    ) -> None:
        if body_order_id is not None and body_order_id != path_order_id:
            raise DomainValidationError("order_id mismatch between path and body")
