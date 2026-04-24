from dataclasses import dataclass


@dataclass
class ProductImageCreateData:
    product_id: int
    storage_key: str


@dataclass
class ProductImage:
    id: int
    product_id: int
    storage_key: str


@dataclass
class ProductImagesDeleteResult:
    product_id: int
    deleted_ids: list[int]
