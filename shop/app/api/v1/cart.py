from fastapi import APIRouter, Body, Depends, Path, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import get_cart_service, get_event_log_service
from shop.app.schemas.cart_item_schemas import CartItemAdd, CartItemQuantityUpdate
from shop.app.schemas.cart_schemas import CartWithItems
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartWithItems)
async def get_current_cart(
    current_user: UserOut = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    return await cart_service.get_cart(current_user.id)


@router.post(
    "/items",
    response_model=CartWithItems,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    request: Request,
    data: CartItemAdd = Body(...),
    current_user: UserOut = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    cart = await cart_service.add_item(current_user.id, data)
    await event_log_service.log_event(
        "CART_ITEM_ADDED",
        user_id=current_user.id,
        description=f"Product #{data.product_id} added to cart",
        request=request,
    )
    return cart


@router.patch("/items/{item_id}", response_model=CartWithItems)
async def update_item_quantity(
    request: Request,
    item_id: int = Path(..., gt=0),
    data: CartItemQuantityUpdate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    cart = await cart_service.update_item_quantity(
        current_user.id,
        item_id,
        data,
    )
    await event_log_service.log_event(
        "CART_ITEM_UPDATED",
        user_id=current_user.id,
        description=f"Cart item #{item_id} quantity updated to {data.quantity}",
        request=request,
    )
    return cart


@router.delete("/items/{item_id}", response_model=CartWithItems)
async def remove_cart_item(
    request: Request,
    item_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    cart = await cart_service.remove_item(current_user.id, item_id)
    await event_log_service.log_event(
        "CART_ITEM_REMOVED",
        user_id=current_user.id,
        description=f"Cart item #{item_id} removed",
        request=request,
    )
    return cart


@router.delete("/", response_model=CartWithItems)
async def clear_cart(
    request: Request,
    current_user: UserOut = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    cart = await cart_service.clear_cart(current_user.id)
    await event_log_service.log_event(
        "CART_CLEARED",
        user_id=current_user.id,
        description="Cart cleared",
        request=request,
    )
    return cart



