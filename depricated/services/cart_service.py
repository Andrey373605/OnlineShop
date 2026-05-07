from decimal import Decimal

from shop.app.core.exceptions import (
    DomainValidationError,
    EntityNotFoundError,
)
from shop.app.domain.entities.product import Product
from shop.app.models.schemas import (
    CartItemAdd,
    CartItemOut,
    CartItemQuantityUpdate,
    CartOut,
    CartWithItems,
)
from shop.app.infrastructure.persistence.postgres.repositories.unit_of_work import SqlUnitOfWork


class CartService:
    def __init__(self, uow: SqlUnitOfWork):
        self._uow = uow

    async def get_cart(self, user_id: int) -> CartWithItems:
        async with self._uow as uow:
            return await self._build_cart_response(uow, cart)

    async def add_item(self, user_id: int, data: CartItemAdd) -> CartWithItems:
        async with self._uow as uow:
            product = await self._get_product_or_raise(uow, data.product_id)
            self._validate_quantity(data.quantity, product)

            existing_item = await uow.cart_items.get_by_cart_and_product(
                cart.id,
                product.id,
            )

            if existing_item:
                updated_quantity = existing_item.quantity + data.quantity
                self._validate_quantity(updated_quantity, product)
                await uow.cart_items.update(
                    existing_item.id,
                    {"quantity": updated_quantity},
                )
            else:
                await uow.cart_items.create(
                    {
                        "cart_id": cart.id,
                        "product_id": product.id,
                        "quantity": data.quantity,
                    }
                )

            await self._recalculate_total(uow, cart.id)
            result = await self._build_cart_response(uow, cart)
            await uow.commit()
            return result

    async def update_item_quantity(
        self,
        user_id: int,
        item_id: int,
        data: CartItemQuantityUpdate,
    ) -> CartWithItems:
        async with self._uow as uow:
            cart_item = await self._get_cart_item_or_raise(uow, item_id, cart.id)
            product = await self._get_product_or_raise(uow, cart_item.product_id)
            self._validate_quantity(data.quantity, product)

            await uow.cart_items.update(
                item_id,
                {"quantity": data.quantity},
            )
            await self._recalculate_total(uow, cart.id)
            result = await self._build_cart_response(uow, cart)
            await uow.commit()
            return result

    async def remove_item(self, user_id: int, item_id: int) -> CartWithItems:
        async with self._uow as uow:
            await self._get_cart_item_or_raise(uow, item_id, cart.id)
            await uow.cart_items.delete(item_id)
            await self._recalculate_total(uow, cart.id)
            result = await self._build_cart_response(uow, cart)
            await uow.commit()
            return result

    async def clear_cart(self, user_id: int) -> CartWithItems:
        async with self._uow as uow:
            await uow.cart_items.delete_by_cart_id(cart.id)
            await uow.carts.update(cart.id, {"total_amount": Decimal("0")})
            result = await self._build_cart_response(uow, cart)
            await uow.commit()
            return result

    @staticmethod
    async def _recalculate_total(uow: SqlUnitOfWork, cart_id: int) -> Decimal:
        items = await uow.cart_items.get_by_cart_id(cart_id)
        total = sum((item.product_price or Decimal("0")) * item.quantity for item in items)
        await uow.carts.update(
            cart_id,
            {"total_amount": total},
        )
        return total

    @staticmethod
    async def _get_product_or_raise(uow: SqlUnitOfWork, product_id: int) -> Product:
        product = await uow.products.get_by_id(product_id)
        if not product:
            raise EntityNotFoundError("Product")
        return product

    @staticmethod
    async def _get_cart_item_or_raise(
        uow: SqlUnitOfWork,
        item_id: int,
        cart_id: int,
    ) -> CartItemOut:
        cart_item = await uow.cart_items.get_by_id(item_id)
        if not cart_item or cart_item.cart_id != cart_id:
            raise EntityNotFoundError("Cart item")
        return cart_item

    @staticmethod
    def _validate_quantity(quantity: int, product: Product) -> None:
        if quantity <= 0:
            raise DomainValidationError("Quantity must be greater than zero")
        if quantity > product.stock:
            raise DomainValidationError("Requested quantity exceeds available stock")
