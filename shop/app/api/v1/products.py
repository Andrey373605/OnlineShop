from fastapi import APIRouter, Depends, Body, Path, Request
from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.pagination import CommonPaginationParams
from shop.app.dependencies.services import get_event_log_service, get_product_service
from shop.app.schemas.product_schemas import ProductResponse, ProductCreate, ProductUpdate
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.product_service import ProductService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix='/products', tags=['Products'])


@router.post("/", response_model=ProductResponse)
async def create_product(request: Request,
                         data: ProductCreate = Body(),
                         current_user: UserOut = Depends(get_current_user),
                         product_service: ProductService = Depends(get_product_service),
                         event_log_service: EventLogService = Depends(get_event_log_service)):
    _ensure_admin(current_user)
    response = await product_service.create_product(data)
    await event_log_service.log_event(
        "PRODUCT_CREATED",
        user_id=current_user.id,
        description=f"Product #{response['id']} created by {current_user.username}",
        request=request,
    )
    return response


@router.get("/{product_id}")
async def get_product_by_id(product_id: int = Path(),
                            product_service: ProductService = Depends(get_product_service)):
    return await product_service.get_product_by_id(product_id)


@router.get("/")
async def get_all_products(product_service: ProductService = Depends(get_product_service),
                           pagination: CommonPaginationParams = Depends(CommonPaginationParams)):
    return await product_service.get_all_products(limit=pagination.limit, offset=pagination.offset)


@router.put("/{product_id}")
async def update_product(request: Request,
                         product_id: int = Path(),
                         data: ProductUpdate = Body(),
                         current_user: UserOut = Depends(get_current_user),
                         product_service: ProductService = Depends(get_product_service),
                         event_log_service: EventLogService = Depends(get_event_log_service)):
    _ensure_admin(current_user)
    response = await product_service.update_product(product_id, data)
    await event_log_service.log_event(
        "PRODUCT_UPDATED",
        user_id=current_user.id,
        description=f"Product #{product_id} updated by {current_user.username}",
        request=request,
    )
    return response


@router.delete("/{product_id}")
async def delete_product(request: Request,
                         product_id: int = Path(),
                         current_user: UserOut = Depends(get_current_user),
                         product_service: ProductService = Depends(get_product_service),
                         event_log_service: EventLogService = Depends(get_event_log_service)):
    _ensure_admin(current_user)
    response = await product_service.delete_product(product_id)
    await event_log_service.log_event(
        "PRODUCT_DELETED",
        user_id=current_user.id,
        description=f"Product #{product_id} deleted by {current_user.username}",
        request=request,
    )
    return response
