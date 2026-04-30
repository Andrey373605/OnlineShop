from dataclasses import dataclass

from shop.app.models.schemas import ProductImageCreate


@dataclass
class ProductImageCreateData:
    product_id: int
    storage_key: str

    @classmethod
    def from_input(cls, data: ProductImageCreate, storage_key: str):
        return cls(
            product_id=data.product_id,
            storage_key=storage_key,
        )


@dataclass
class ProductImageUpdateData:
    product_id: int | None = None
    storage_key: str | None = None


@dataclass
class ProductImage:
    id: int
    product_id: int
    storage_key: str


@dataclass
class ProductImagesDeleteResult:
    product_id: int
    deleted_ids: list[int]
