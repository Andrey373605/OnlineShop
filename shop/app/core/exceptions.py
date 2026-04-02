class AppError(Exception):
    """Базовое доменное исключение приложения."""

    def __init__(self, message: str = "An application error occurred"):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Запрашиваемый ресурс не найден."""

    def __init__(self, resource: str = "Resource", message: str | None = None):
        self.resource = resource
        super().__init__(message or f"{resource} not found")


class AlreadyExistsError(AppError):
    """Ресурс с такими данными уже существует."""

    def __init__(self, resource: str = "Resource", message: str | None = None):
        self.resource = resource
        super().__init__(message or f"{resource} already exists")


class OperationFailedError(AppError):
    """Внутренняя операция завершилась неуспешно."""

    pass


class ServiceUnavailableError(AppError):
    """Зависимый сервис или ресурс недоступен."""

    pass


class AuthenticationError(AppError):
    """Ошибка аутентификации."""

    pass


class PermissionDeniedError(AppError):
    """Недостаточно прав для выполнения операции."""

    pass


class DomainValidationError(AppError):
    """Нарушение бизнес-правила валидации."""

    pass


class S3Error(AppError):
    """Ошибка S3"""

    pass


class S3UploadError(S3Error):
    """Ошибка загрузки в S3"""

    pass


class S3DeleteError(S3Error):
    """Ошибка удаления из S3"""

    pass
