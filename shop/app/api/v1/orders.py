from fastapi import APIRouter, Body, Depends, Path, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.pagination import CommonPaginationParams
from shop.app.dependencies.services import (
    get_event_log_service,
    get_order_item_service,
    get_order_service,
)
from shop.app.schemas.order_item_schemas import (
    OrderItemCreate,
    OrderItemOut,
    OrderItemUpdate,
)
from shop.app.schemas.order_schemas import OrderCreate, OrderOut, OrderUpdate
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.order_item_service import OrderItemService
from shop.app.services.order_service import OrderService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/orders", tags=["Orders"])



@router.get("/", response_model=list[OrderOut])
async def list_orders(
    pagination: CommonPaginationParams = Depends(CommonPaginationParams),
    current_user: UserOut = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> list[OrderOut]:
    _ensure_admin(current_user)
    return await order_service.list_orders(
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{order_id}", response_model=OrderOut)
async def get_order_by_id(
    order_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderOut:
    _ensure_admin(current_user)
    return await order_service.get_order_by_id(order_id)


@router.post(
    "/",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    request: Request,
    data: OrderCreate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> OrderOut:
    _ensure_admin(current_user)
    order = await order_service.create_order(data)
    await event_log_service.log_event(
        "ORDER_CREATED",
        user_id=current_user.id,
        description=f"Order #{order.id} created by {current_user.username}",
        request=request,
    )
    return order


@router.put("/{order_id}", response_model=OrderOut)
async def update_order(
    request: Request,
    order_id: int = Path(..., gt=0),
    data: OrderUpdate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> OrderOut:
    _ensure_admin(current_user)
    order = await order_service.update_order(order_id, data)
    await event_log_service.log_event(
        "ORDER_UPDATED",
        user_id=current_user.id,
        description=f"Order #{order_id} updated by {current_user.username}",
        request=request,
    )
    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
    request: Request,
    order_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    _ensure_admin(current_user)
    await order_service.delete_order(order_id)
    await event_log_service.log_event(
        "ORDER_DELETED",
        user_id=current_user.id,
        description=f"Order #{order_id} deleted by {current_user.username}",
        request=request,
    )


@router.get(
    "/{order_id}/items",
    response_model=list[OrderItemOut],
)
async def list_order_items(
    order_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    item_service: OrderItemService = Depends(get_order_item_service),
) -> list[OrderItemOut]:
    _ensure_admin(current_user)
    return await item_service.list_order_items(order_id)


@router.post(
    "/{order_id}/items",
    response_model=OrderItemOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_item(
    request: Request,
    order_id: int = Path(..., gt=0),
    data: OrderItemCreate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    item_service: OrderItemService = Depends(get_order_item_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> OrderItemOut:
    _ensure_admin(current_user)
    item = await item_service.create_order_item(order_id, data)
    await event_log_service.log_event(
        "ORDER_ITEM_CREATED",
        user_id=current_user.id,
        description=f"Item #{item.id} added to order #{order_id}",
        request=request,
    )
    return item


@router.get(
    "/{order_id}/items/{item_id}",
    response_model=OrderItemOut,
)
async def get_order_item(
    order_id: int = Path(..., gt=0),
    item_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    item_service: OrderItemService = Depends(get_order_item_service),
) -> OrderItemOut:
    _ensure_admin(current_user)
    return await item_service.get_order_item(order_id, item_id)


@router.put(
    "/{order_id}/items/{item_id}",
    response_model=OrderItemOut,
)
async def update_order_item(
    request: Request,
    order_id: int = Path(..., gt=0),
    item_id: int = Path(..., gt=0),
    data: OrderItemUpdate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    item_service: OrderItemService = Depends(get_order_item_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> OrderItemOut:
    _ensure_admin(current_user)
    item = await item_service.update_order_item(order_id, item_id, data)
    await event_log_service.log_event(
        "ORDER_ITEM_UPDATED",
        user_id=current_user.id,
        description=f"Item #{item_id} in order #{order_id} updated",
        request=request,
    )
    return item


@router.delete(
    "/{order_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order_item(
    request: Request,
    order_id: int = Path(..., gt=0),
    item_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    item_service: OrderItemService = Depends(get_order_item_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    _ensure_admin(current_user)
    await item_service.delete_order_item(order_id, item_id)
    await event_log_service.log_event(
        "ORDER_ITEM_DELETED",
        user_id=current_user.id,
        description=f"Item #{item_id} removed from order #{order_id}",
        request=request,
    )



