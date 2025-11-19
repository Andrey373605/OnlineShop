from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ProductSpecificationBase(BaseModel):
    product_id: int
    specifications: dict[str, Any]


class ProductSpecificationCreate(ProductSpecificationBase):
    pass


class ProductSpecificationUpdate(BaseModel):
    product_id: int | None = None
    specifications: dict[str, Any] | None = None


class ProductSpecificationOut(ProductSpecificationBase):
    id: int
    created_at: datetime
    updated_at: datetime




