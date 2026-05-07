from shop.app.domain.errors import (
    ExceedsAvailableStockError,
    InvalidQuantityTypeError,
    NonPositiveQuantityError,
)


def validate_line_quantity(quantity: int) -> None:
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise InvalidQuantityTypeError("Quantity must be an integer")
    if quantity < 1:
        raise NonPositiveQuantityError("Quantity must be at least 1")


def validate_max_stock(quantity: int, max_stock: int | None) -> None:
    if max_stock is not None and quantity > max_stock:
        raise ExceedsAvailableStockError(quantity, max_stock)
