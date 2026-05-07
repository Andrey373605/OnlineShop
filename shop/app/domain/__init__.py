"""Domain model package (entities and value objects)."""

from shop.app.domain.attributes import coerce_attributes_dict
from shop.app.domain.enums import MovementReason, OrderStatus, PaymentStatus
from shop.app.domain.entities.brand import Brand
from shop.app.domain.entities.cart import Cart, CartItem, validate_line_quantity, validate_max_stock
from shop.app.domain.entities.category import Category, CategoryCreateData, CategoryUpdateData
from shop.app.domain.entities.order import Order, OrderItem
from shop.app.domain.entities.permission import Permission
from shop.app.domain.entities.product import Product, ProductCreateData, ProductUpdateData
from shop.app.domain.entities.product_details import ProductDetails
from shop.app.domain.entities.product_image import ProductImage
from shop.app.domain.entities.product_variant import ProductVariant
from shop.app.domain.entities.product_variant_details import ProductVariantDetails
from shop.app.domain.entities.review import Review
from shop.app.domain.entities.role import Role
from shop.app.domain.entities.stock_movement import StockMovement
from shop.app.domain.entities.user import User
from shop.app.domain.entities.warehouse import Warehouse
from shop.app.domain.services import (
    AccessPolicyDomainService,
    CatalogPolicyDomainService,
    CheckoutPolicyDomainService,
    DiscountPolicyDomainService,
    InventoryAllocationDomainService,
    ReviewPolicyDomainService,
)
from shop.app.domain.value_objects import (
    Email,
    FullName,
    OrderNumber,
    PaymentMethod,
    Price,
    Rating,
    ReviewDescription,
    ReviewTitle,
    ShippingAddress,
    Sku,
    StorageKey,
    Username,
    normalize_review_description,
    quantize_money_amount,
)

__all__ = [
    "Brand",
    "Cart",
    "CartItem",
    "Category",
    "CategoryCreateData",
    "CategoryUpdateData",
    "MovementReason",
    "Order",
    "OrderItem",
    "OrderStatus",
    "PaymentStatus",
    "Permission",
    "Price",
    "Product",
    "ProductCreateData",
    "ProductUpdateData",
    "ProductDetails",
    "ProductImage",
    "ProductVariant",
    "ProductVariantDetails",
    "Review",
    "Role",
    "StockMovement",
    "User",
    "Warehouse",
    "coerce_attributes_dict",
    "quantize_money_amount",
    "Username",
    "Email",
    "FullName",
    "Rating",
    "ReviewTitle",
    "ReviewDescription",
    "OrderNumber",
    "ShippingAddress",
    "PaymentMethod",
    "Sku",
    "StorageKey",
    "normalize_review_description",
    "validate_line_quantity",
    "validate_max_stock",
    "AccessPolicyDomainService",
    "CatalogPolicyDomainService",
    "CheckoutPolicyDomainService",
    "DiscountPolicyDomainService",
    "InventoryAllocationDomainService",
    "ReviewPolicyDomainService",
]
