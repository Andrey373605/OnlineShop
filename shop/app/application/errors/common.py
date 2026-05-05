from shop.app.application.errors.base import ApplicationError


class InvalidCommandError(ApplicationError):
    code = "invalid_command"


class NotFoundError(ApplicationError):
    code = "not_found"


class PermissionDeniedError(ApplicationError):
    code = "permission_denied"


class ConflictError(ApplicationError):
    code = "conflict"


class ConcurrencyError(ApplicationError):
    code = "concurrency_error"


class ApplicationServiceUnavailableError(ApplicationError):
    code = "service_unavailable"
