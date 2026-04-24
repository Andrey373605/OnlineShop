from pydantic import BaseModel


class ProductImageCreate(BaseModel):
    product_id: int


class ProductImageOut(BaseModel):
    id: int
    product_id: int
    image_url: str


class ProductImageResponse(BaseModel):
    id: int
    message: str


class ProductImagesDeleteResponse(BaseModel):
    product_id: int
    deleted_ids: list[int]
