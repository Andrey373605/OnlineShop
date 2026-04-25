from shop.app.core.exceptions import AppError


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
