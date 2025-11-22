from fastapi import HTTPException, status

from shop.app.repositories.order_item_repository import OrderItemRepository
from shop.app.repositories.order_repository import OrderRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.schemas.order_item_schemas import (
    OrderItemCreate,
    OrderItemOut,
    OrderItemUpdate,
)
from shop.app.schemas.order_schemas import OrderOut
from shop.app.schemas.product_schemas import ProductOut


class OrderItemService:
    def __init__(
        self,
        order_repo: OrderRepository,
        order_item_repo: OrderItemRepository,
        product_repo: ProductRepository,
    ):
        self.order_repo = order_repo
        self.order_item_repo = order_item_repo
        self.product_repo = product_repo

    async def list_order_items(self, order_id: int) -> list[OrderItemOut]:
        await self._get_order_or_404(order_id)
        return await self.order_item_repo.get_by_order_id(order_id)

    async def get_order_item(self, order_id: int, item_id: int) -> OrderItemOut:
        item = await self._get_item_or_404(item_id)
        if item.order_id != order_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order item not found",
            )
        return item

    async def create_order_item(
        self,
        order_id: int,
        data: OrderItemCreate,
    ) -> OrderItemOut:
        self._validate_order_item_request(order_id, data.order_id)
        await self._get_order_or_404(order_id)
        await self._get_product_or_404(data.product_id)

        payload = data.model_dump()
        payload["order_id"] = order_id

        item_id = await self.order_item_repo.create(payload)
        return await self._get_item_or_500(item_id, detail="Unable to fetch created order item")

    async def update_order_item(
        self,
        order_id: int,
        item_id: int,
        data: OrderItemUpdate,
    ) -> OrderItemOut:
        item = await self.get_order_item(order_id, item_id)

        if data.order_id is not None and data.order_id != order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move order item to another order",
            )

        if data.product_id is not None and data.product_id != item.product_id:
            await self._get_product_or_404(data.product_id)

        update_payload = data.model_dump(exclude_unset=True)
        update_payload["order_id"] = order_id

        updated = await self.order_item_repo.update(item_id, update_payload)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update order item",
            )

        return await self._get_item_or_500(item_id, detail="Unable to fetch updated order item")

    async def delete_order_item(self, order_id: int, item_id: int) -> None:
        await self.get_order_item(order_id, item_id)

        deleted = await self.order_item_repo.delete(item_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete order item",
            )

    async def _get_order_or_404(self, order_id: int) -> OrderOut:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return order

    async def _get_product_or_404(self, product_id: int) -> ProductOut:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

    async def _get_item_or_404(self, item_id: int) -> OrderItemOut:
        item = await self.order_item_repo.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order item not found",
            )
        return item

    async def _get_item_or_500(self, item_id: int, detail: str) -> OrderItemOut:
        item = await self.order_item_repo.get_by_id(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail,
            )
        return item

    @staticmethod
    def _validate_order_item_request(
        path_order_id: int,
        body_order_id: int | None,
    ) -> None:
        if body_order_id is not None and body_order_id != path_order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="order_id mismatch between path and body",
            )



