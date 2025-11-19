from pydantic import BaseModel, AnyUrl


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




