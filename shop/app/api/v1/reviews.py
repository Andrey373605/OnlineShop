from fastapi import APIRouter, Body, Depends, Path, Request, status

from shop.app.dependencies.auth import get_current_user
from shop.app.dependencies.pagination import CommonPaginationParams
from shop.app.dependencies.services import get_event_log_service, get_review_service
from shop.app.schemas.review_schemas import ReviewCreate, ReviewOut, ReviewUpdate
from shop.app.schemas.user_schemas import UserOut
from shop.app.services.event_log_service import EventLogService
from shop.app.services.review_service import ReviewService
from shop.app.utils.ensure_admin import is_admin

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=list[ReviewOut])
async def list_reviews(
    pagination: CommonPaginationParams = Depends(CommonPaginationParams),
    review_service: ReviewService = Depends(get_review_service),
) -> list[ReviewOut]:
    return await review_service.list_reviews(
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{review_id}", response_model=ReviewOut)
async def get_review_by_id(
    review_id: int = Path(..., gt=0),
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewOut:
    return await review_service.get_review_by_id(review_id)


@router.post(
    "/",
    response_model=ReviewOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    request: Request,
    payload: ReviewCreate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> ReviewOut:
    review = await review_service.create_review(
        user_id=current_user.id,
        data=payload,
    )
    await event_log_service.log_event(
        "REVIEW_CREATED",
        user_id=current_user.id,
        description=f"Review #{review.id} created for product #{review.product_id}",
        request=request,
    )
    return review


@router.put(
    "/{review_id}",
    response_model=ReviewOut,
)
async def update_review(
    request: Request,
    review_id: int = Path(..., gt=0),
    payload: ReviewUpdate = Body(...),
    current_user: UserOut = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> ReviewOut:
    review = await review_service.update_review(
        review_id=review_id,
        user_id=current_user.id,
        data=payload,
        is_admin=is_admin(current_user),
    )
    await event_log_service.log_event(
        "REVIEW_UPDATED",
        user_id=current_user.id,
        description=f"Review #{review_id} updated by {current_user.username}",
        request=request,
    )
    return review


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    request: Request,
    review_id: int = Path(..., gt=0),
    current_user: UserOut = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service),
    event_log_service: EventLogService = Depends(get_event_log_service),
) -> None:
    await review_service.delete_review(
        review_id=review_id,
        user_id=current_user.id,
        is_admin=is_admin(current_user),
    )
    await event_log_service.log_event(
        "REVIEW_DELETED",
        user_id=current_user.id,
        description=f"Review #{review_id} deleted by {current_user.username}",
        request=request,
    )


