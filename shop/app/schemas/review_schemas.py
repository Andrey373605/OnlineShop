from datetime import datetime

from pydantic import BaseModel


class ReviewBase(BaseModel):
    product_id: int
    title: str
    description: str | None = None
    rating: int


class ReviewCreate(ReviewBase):
    ...


class ReviewUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    rating: int | None = None


class ReviewOut(ReviewBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    username: str | None = None
    product_title: str | None = None




