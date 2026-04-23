from pydantic import BaseModel


class ProductImageBase(BaseModel):
    product_id: int


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageUpdate(BaseModel):
    pass


class ProductImageOut(ProductImageBase):
    id: int
    storage_key: str


class ProductImageResponse(BaseModel):
    id: int
    message: str


class ProductImagesDeleteResponse(BaseModel):
    product_id: int
    deleted_ids: list[int]
