from shop.app.models.domain.product import Product
from shop.app.models.schemas import ProductOut
from shop.app.services.media_url_builder import MediaUrlBuilder


class ProductPresenter:
    def __init__(self, media_url_builder: MediaUrlBuilder):
        self._media_url_builder = media_url_builder

    def to_out(self, product: Product) -> ProductOut:
        return ProductOut(
            id=product.id,
            title=product.title,
            description=product.description,
            price=product.price,
            stock=product.stock,
            brand=product.brand,
            is_published=product.is_published,
            category_id=product.category_id,
            thumbnail_url=self._media_url_builder.build(product.thumbnail_key),
        )

    def to_out_list(self, products: list[Product]) -> list[ProductOut]:
        return [self.to_out(product) for product in products]
