from dataclasses import dataclass


@dataclass
class ProductImageCreateData:
    product_id: int
    storage_key: str
