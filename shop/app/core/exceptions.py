class AppError(Exception):
    message: str
    code: str = "internal_server_error"
    status_code: int = 500

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class EntityNotFoundError(AppError):
    code = "entity_not_found"
    status_code = 404


class ConflictError(AppError):
    code = "conflict_error"
    status_code = 409


class DomainValidationError(AppError):
    code = "validation_error"
    status_code = 400


class ApplicationUnavailableError(AppError):
    code = "application_unavailable"
    status_code = 503


# Storage
class StorageError(AppError):
    code = "storage_error"
    status_code = 500


class StorageValidationError(StorageError):
    code = "storage_validation_failed"
    status_code = 400


class StorageUnavailableError(StorageError):
    code = "storage_unavailable"
    status_code = 503


class StorageObjectNotFoundError(StorageError):
    code = "storage_object_not_found"
    status_code = 404
