from dataclasses import dataclass


@dataclass
class ProductImageCreateData:
    product_id: int
    image_path: str
