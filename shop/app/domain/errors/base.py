

class DomainError(Exception):
    """Base class for all domain-level business rule violations."""


class DomainValidationError(DomainError):
    """Generic domain validation error when no specific type exists."""
