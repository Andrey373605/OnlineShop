from decimal import Decimal

from fastapi import HTTPException, status

from shop.app.repositories.cart_item_repository import CartItemRepository
from shop.app.repositories.cart_repository import CartRepository
from shop.app.repositories.product_repository import ProductRepository
from shop.app.schemas.cart_item_schemas import CartItemAdd, CartItemQuantityUpdate, CartItemOut
from shop.app.schemas.cart_schemas import CartWithItems, CartOut
from shop.app.schemas.product_schemas import ProductOut


class CartService:
    def __init__(
        self,
        cart_repo: CartRepository,
        cart_item_repo: CartItemRepository,
        product_repo: ProductRepository,
    ):
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo
        self.product_repo = product_repo

    async def get_cart(self, user_id: int) -> CartWithItems:
        cart = await self._ensure_cart(user_id)
        return await self._build_cart_response(cart)

    async def add_item(self, user_id: int, data: CartItemAdd) -> CartWithItems:
        cart = await self._ensure_cart(user_id)
        product = await self._get_product_or_404(data.product_id)
        self._validate_quantity(data.quantity, product)

        existing_item = await self.cart_item_repo.get_by_cart_and_product(
            cart.id,
            product.id,
        )

        if existing_item:
            updated_quantity = existing_item.quantity + data.quantity
            self._validate_quantity(updated_quantity, product)
            await self.cart_item_repo.update(
                existing_item.id,
                {"quantity": updated_quantity},
            )
        else:
            await self.cart_item_repo.create(
                {
                    "cart_id": cart.id,
                    "product_id": product.id,
                    "quantity": data.quantity,
                }
            )

        await self._recalculate_total(cart.id)
        return await self._build_cart_response(cart)

    async def update_item_quantity(
        self,
        user_id: int,
        item_id: int,
        data: CartItemQuantityUpdate,
    ) -> CartWithItems:
        cart = await self._ensure_cart(user_id)
        cart_item = await self._get_cart_item_or_404(item_id, cart.id)
        product = await self._get_product_or_404(cart_item.product_id)
        self._validate_quantity(data.quantity, product)

        await self.cart_item_repo.update(
            item_id,
            {"quantity": data.quantity},
        )
        await self._recalculate_total(cart.id)
        return await self._build_cart_response(cart)

    async def remove_item(self, user_id: int, item_id: int) -> CartWithItems:
        cart = await self._ensure_cart(user_id)
        await self._get_cart_item_or_404(item_id, cart.id)
        await self.cart_item_repo.delete(item_id)
        await self._recalculate_total(cart.id)
        return await self._build_cart_response(cart)

    async def clear_cart(self, user_id: int) -> CartWithItems:
        cart = await self._ensure_cart(user_id)
        await self.cart_item_repo.delete_by_cart_id(cart.id)
        await self.cart_repo.update(cart.id, {"total_amount": Decimal("0")})
        return await self._build_cart_response(cart)

    async def _ensure_cart(self, user_id: int) -> CartOut:
        cart = await self.cart_repo.get_by_user_id(user_id)
        if cart:
            return cart
        cart_id = await self.cart_repo.create(
            {
                "user_id": user_id,
                "total_amount": Decimal("0"),
            }
        )
        created_cart = await self.cart_repo.get_by_id(cart_id)
        if not created_cart:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create cart",
            )
        return created_cart

    async def _build_cart_response(self, cart: CartOut) -> CartWithItems:
        fresh_cart = await self.cart_repo.get_by_id(cart.id) or cart
        items = await self.cart_item_repo.get_by_cart_id(cart.id)
        return CartWithItems(**fresh_cart.model_dump(), items=items)

    async def _recalculate_total(self, cart_id: int) -> Decimal:
        items = await self.cart_item_repo.get_by_cart_id(cart_id)
        total = sum(
            (item.product_price or Decimal("0")) * item.quantity
            for item in items
        )
        await self.cart_repo.update(
            cart_id,
            {"total_amount": total},
        )
        return total

    async def _get_product_or_404(self, product_id: int) -> ProductOut:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

    async def _get_cart_item_or_404(
        self,
        item_id: int,
        cart_id: int,
    ) -> CartItemOut:
        cart_item = await self.cart_item_repo.get_by_id(item_id)
        if not cart_item or cart_item.cart_id != cart_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found",
            )
        return cart_item

    @staticmethod
    def _validate_quantity(quantity: int, product: ProductOut) -> None:
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero",
            )
        if quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock",
            )

