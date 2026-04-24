from shop.app.models.domain.product_image import ProductImage
from shop.app.models.schemas import ProductImageOut
from shop.app.services.media_url_builder import MediaUrlBuilder


class ProductImagePresenter:
    def __init__(self, media_url_builder: MediaUrlBuilder):
        self._media_url_builder = media_url_builder

    def to_out(self, image: ProductImage) -> ProductImageOut:
        return ProductImageOut(
            id=image.id,
            product_id=image.product_id,
            image_url=self._media_url_builder.build(image.storage_key),
        )

    def to_out_list(self, images: list[ProductImage]) -> list[ProductImageOut]:
        return [self.to_out(image) for image in images]
