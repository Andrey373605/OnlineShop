from fastapi import APIRouter, Body, Depends, Path, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import (
    get_event_log_service,
    get_product_specification_service,
)
from shop.app.schemas.product_specification_schemas import (
    ProductSpecificationCreate,
    ProductSpecificationOut,
    ProductSpecificationResponse,
    ProductSpecificationUpdate,
)
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.product_specification_service import (
    ProductSpecificationService,
)
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/product-specifications", tags=["Product Specifications"])


@router.post(
    "/",
    response_model=ProductSpecificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_specification(
        request: Request,
        data: ProductSpecificationCreate = Body(...),
        current_user: UserOut = Depends(get_current_user),
        service: ProductSpecificationService = Depends(get_product_specification_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.create_specification(data)
    await event_log_service.log_event(
        "PRODUCT_SPECIFICATION_CREATED",
        user_id=current_user.id,
        description=f"Specification #{response.id} created for product #{data.product_id}",
        request=request,
    )
    return response


@router.get(
    "/",
    response_model=list[ProductSpecificationOut],
)
async def list_product_specifications(
        service: ProductSpecificationService = Depends(get_product_specification_service),
):
    return await service.get_all_specifications()


@router.get(
    "/{specification_id}",
    response_model=ProductSpecificationOut,
)
async def get_product_specification(
        specification_id: int = Path(..., gt=0),
        service: ProductSpecificationService = Depends(get_product_specification_service),
):
    return await service.get_specification_by_id(specification_id)


@router.get(
    "/product/{product_id}",
    response_model=ProductSpecificationOut,
)
async def get_product_specification_by_product(
        product_id: int = Path(..., gt=0),
        service: ProductSpecificationService = Depends(get_product_specification_service),
):
    return await service.get_specification_by_product_id(product_id)


@router.put(
    "/{specification_id}",
    response_model=ProductSpecificationResponse,
)
async def update_product_specification(
        request: Request,
        specification_id: int = Path(..., gt=0),
        data: ProductSpecificationUpdate = Body(...),
        current_user: UserOut = Depends(get_current_user),
        service: ProductSpecificationService = Depends(get_product_specification_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.update_specification(specification_id, data)
    await event_log_service.log_event(
        "PRODUCT_SPECIFICATION_UPDATED",
        user_id=current_user.id,
        description=f"Specification #{specification_id} updated by {current_user.username}",
        request=request,
    )
    return response


@router.delete(
    "/{specification_id}",
    response_model=ProductSpecificationResponse,
)
async def delete_product_specification(
        request: Request,
        specification_id: int = Path(..., gt=0),
        current_user: UserOut = Depends(get_current_user),
        service: ProductSpecificationService = Depends(get_product_specification_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.delete_specification(specification_id)
    await event_log_service.log_event(
        "PRODUCT_SPECIFICATION_DELETED",
        user_id=current_user.id,
        description=f"Specification #{specification_id} deleted by {current_user.username}",
        request=request,
    )
    return response
