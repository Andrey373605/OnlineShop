
from enum import StrEnum


class MovementReason(StrEnum):
    RECEIPT = "receipt"
    SALE = "sale"
    CANCELLATION = "cancel"
    CORRECTION = "correction"


__all__ = ["MovementReason"]

