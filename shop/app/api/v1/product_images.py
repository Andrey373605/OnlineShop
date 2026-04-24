from fastapi import APIRouter, Depends, File, Form, Path, Request, UploadFile, status, Header

from shop.app.api.mappers.uploads import map_upload_file
from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.services import (
    get_event_log_service,
    get_product_image_service,
    get_product_image_presenter,
)
from shop.app.models.schemas import (
    ProductImageCreate,
    ProductImageOut,
    ProductImageResponse,
    ProductImagesDeleteResponse,
    UserOut,
)
from shop.app.presenters.product_image_presenter import ProductImagePresenter
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
    product_id: int = Form(...),
    file: UploadFile = File(...),
    content_length: int = Header(None),
    current_user: UserOut = Depends(get_current_user),
    service: ProductImageService = Depends(get_product_image_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
    presenter: ProductImagePresenter = Depends(get_product_image_presenter),
):
    _ensure_admin(current_user)
    data = ProductImageCreate(product_id=product_id)
    source = map_upload_file(file, content_length)
    image = await service.create_image(data, source)

    await event_log_service.log_event(
        "PRODUCT_IMAGE_CREATED",
        user_id=current_user.id,
        description=f"Image #{image.id} created for product #{data.product_id}",
        request=request,
    )

    return presenter.to_out(image)


@router.get(
    "/{image_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductImageOut,
)
async def get_product_image(
    image_id: int = Path(..., gt=0),
    service: ProductImageService = Depends(get_product_image_service),
    presenter: ProductImagePresenter = Depends(get_product_image_presenter),
):
    image = await service.get_image_by_id(image_id)
    return presenter.to_out(image)


@router.get(
    "/product/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=list[ProductImageOut],
)
async def get_product_images_by_product(
    product_id: int = Path(..., gt=0),
    service: ProductImageService = Depends(get_product_image_service),
    presenter: ProductImagePresenter = Depends(get_product_image_presenter),
):
    images = await service.get_images_by_product_id(product_id)
    return presenter.to_out_list(images)


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_product_image(
    request: Request,
    image_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    service: ProductImageService = Depends(get_product_image_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
):
    _ensure_admin(current_user)
    await service.delete_image(image_id)

    await event_log_service.log_event(
        "PRODUCT_IMAGE_DELETED",
        user_id=current_user.id,
        description=f"Image #{image_id} deleted by {current_user.username}",
        request=request,
    )


@router.delete(
    "/product/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
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
    result = await service.delete_images_by_product_id(product_id)

    await event_log_service.log_event(
        "PRODUCT_IMAGE_BULK_DELETED",
        user_id=current_user.id,
        description=f"Images for product #{product_id} " f"deleted by {current_user.username}",
        request=request,
    )

    return ProductImagesDeleteResponse(product_id=result.product_id, deleted_ids=result.deleted_ids)
