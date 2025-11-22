from pydantic import BaseModel


class ProductImageBase(BaseModel):
    product_id: int
    image_path: str


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    product_id: int | None = None
    image_path: str | None = None


class ProductImageOut(ProductImageBase):
    id: int


class ProductImageResponse(BaseModel):
    id: int
    message: str


class ProductImagesDeleteResponse(BaseModel):
    product_id: int
    deleted_ids: list[int]






