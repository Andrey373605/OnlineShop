class RepositoryError(Exception):
    """Base error for persistence layer."""


class RepositoryUnavailableError(RepositoryError):
    """Database is unavailable."""


class RepositoryForeignKeyError(RepositoryError):
    """Foreign key constraint violation in persistence layer."""


class RepositoryUniqueConstraintError(RepositoryError):
    """Unique constraint violation in persistence layer."""


class RepositoryRecordNotFoundError(RepositoryError):
    """Expected record was not found in persistence layer."""


class RepositoryMappingError(RepositoryError):
    """Database row cannot be mapped to domain object."""


class RepositoryUnexpectedResultError(RepositoryError):
    """Query failed unexpectedly."""
