
from collections.abc import Sequence

from shop.app.domain import Product, ProductDetails, ProductImage, ProductVariant, ProductVariantDetails


class CatalogPolicyDomainService:
    """Checks publication rules spanning product, details, variants, and media."""

    def ensure_product_ready_for_publish(
        self,
        product: Product,
        details: ProductDetails | None,
        variants: Sequence[ProductVariant],
        variant_details: Sequence[ProductVariantDetails],
        images: Sequence[ProductImage],
    ) -> None:
        """Validate catalog completeness before product publication."""
        raise NotImplementedError("Domain service is not implemented yet")


__all__ = ["CatalogPolicyDomainService"]

