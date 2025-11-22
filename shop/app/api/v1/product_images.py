from fastapi import APIRouter, Body, Depends, Path, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import (
    get_event_log_service,
    get_product_image_service,
)
from shop.app.schemas.product_image_schemas import (
    ProductImageCreate,
    ProductImageOut,
    ProductImageResponse,
    ProductImageUpdate,
    ProductImagesDeleteResponse,
)
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.product_image_service import ProductImageService
from shop.app.utils.ensure_admin import _ensure_admin

router = APIRouter(prefix="/product-images", tags=["Product Images"])


@router.post(
    "/",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_image(
        request: Request,
        data: ProductImageCreate = Body(...),
        current_user: UserOut = Depends(get_current_user),
        service: ProductImageService = Depends(get_product_image_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.create_image(data)
    await event_log_service.log_event(
        "PRODUCT_IMAGE_CREATED",
        user_id=current_user.id,
        description=f"Image #{response.id} created for product #{data.product_id}",
        request=request,
    )
    return response


@router.get(
    "/{image_id}",
    response_model=ProductImageOut,
)
async def get_product_image(
        image_id: int = Path(..., gt=0),
        service: ProductImageService = Depends(get_product_image_service),
):
    return await service.get_image_by_id(image_id)


@router.get(
    "/product/{product_id}",
    response_model=list[ProductImageOut],
)
async def get_product_images_by_product(
        product_id: int = Path(..., gt=0),
        service: ProductImageService = Depends(get_product_image_service),
):
    return await service.get_images_by_product_id(product_id)


@router.put(
    "/{image_id}",
    response_model=ProductImageResponse,
)
async def update_product_image(
        request: Request,
        image_id: int = Path(..., gt=0),
        data: ProductImageUpdate = Body(...),
        current_user: UserOut = Depends(get_current_user),
        service: ProductImageService = Depends(get_product_image_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.update_image(image_id, data)
    await event_log_service.log_event(
        "PRODUCT_IMAGE_UPDATED",
        user_id=current_user.id,
        description=f"Image #{image_id} updated by {current_user.username}",
        request=request,
    )
    return response


@router.delete(
    "/{image_id}",
    response_model=ProductImageResponse,
)
async def delete_product_image(
        request: Request,
        image_id: int = Path(..., gt=0),
        current_user: UserOut = Depends(get_current_user),
        service: ProductImageService = Depends(get_product_image_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.delete_image(image_id)
    await event_log_service.log_event(
        "PRODUCT_IMAGE_DELETED",
        user_id=current_user.id,
        description=f"Image #{image_id} deleted by {current_user.username}",
        request=request,
    )
    return response


@router.delete(
    "/product/{product_id}",
    response_model=ProductImagesDeleteResponse,
)
async def delete_product_images_by_product(
        request: Request,
        product_id: int = Path(..., gt=0),
        current_user: UserOut = Depends(get_current_user),
        service: ProductImageService = Depends(get_product_image_service),
        event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    response = await service.delete_images_by_product_id(product_id)
    await event_log_service.log_event(
        "PRODUCT_IMAGE_BULK_DELETED",
        user_id=current_user.id,
        description=f"Images for product #{product_id} deleted by {current_user.username}",
        request=request,
    )
    return response
