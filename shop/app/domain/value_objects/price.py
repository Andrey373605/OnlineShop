
from decimal import Decimal, ROUND_HALF_UP

from shop.app.domain.errors import DomainValidationError

_MAX_FRACTION_DIGITS = 4


def quantize_money_amount(amount: Decimal) -> Decimal:
    step = Decimal("1").scaleb(-_MAX_FRACTION_DIGITS)
    return amount.quantize(step, rounding=ROUND_HALF_UP)


def _fraction_digit_count(amount: Decimal) -> int:
    normalized = amount.normalize()
    exp = normalized.as_tuple().exponent
    if exp >= 0:
        return 0
    return -exp


class Price:
    """Money value object: amount + ISO currency."""

    def __init__(self, amount: Decimal, currency: str) -> None:
        if not isinstance(amount, Decimal):
            raise DomainValidationError("Amount must be Decimal")
        if not amount.is_finite():
            raise DomainValidationError("Price amount must be a finite number")
        if _fraction_digit_count(amount) > _MAX_FRACTION_DIGITS:
            raise DomainValidationError(
                f"Price amount must have at most {_MAX_FRACTION_DIGITS} decimal places",
            )
        if amount < 0:
            raise DomainValidationError("Price amount cannot be negative")
        if not isinstance(currency, str):
            raise DomainValidationError("Currency must be a string")
        code = currency.strip().upper()
        if len(code) != 3:
            raise DomainValidationError("Currency must be a 3-letter ISO 4217 code")

        self._amount = amount
        self._currency = code

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> str:
        return self._currency

    def with_amount(self, new_amount: Decimal) -> Price:
        return Price(new_amount, self._currency)

    def times_quantity(self, quantity: int) -> Price:
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise DomainValidationError("Quantity must be an integer")
        if quantity < 1:
            raise DomainValidationError("Quantity must be at least 1")
        product = quantize_money_amount(self._amount * quantity)
        return Price(product, self._currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Price):
            return NotImplemented
        return self._amount == other._amount and self._currency == other._currency

    def __hash__(self) -> int:
        return hash((self._amount, self._currency))

    def __repr__(self) -> str:
        return f"<Price {self._amount} {self._currency}>"


__all__ = ["Price", "quantize_money_amount"]

