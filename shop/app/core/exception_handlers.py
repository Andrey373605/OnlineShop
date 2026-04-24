from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shop.app.core.exceptions import (
    AlreadyExistsError,
    AppError,
    AuthenticationError,
    DomainValidationError,
    NotFoundError,
    OperationFailedError,
    PermissionDeniedError,
    ServiceUnavailableError,
    StorageUnavailableError,
    StorageValidationError,
)

_STATUS_MAP: dict[type[AppError], int] = {
    NotFoundError: 404,
    AlreadyExistsError: 400,
    DomainValidationError: 400,
    AuthenticationError: 401,
    PermissionDeniedError: 403,
    OperationFailedError: 500,
    ServiceUnavailableError: 503,
    # Storage
    StorageUnavailableError: 503,
    StorageValidationError: 400,
}


def _status_for(exc: AppError) -> int:
    for cls in type(exc).__mro__:
        if cls in _STATUS_MAP:
            return _STATUS_MAP[cls]
    return 500


async def _app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=_status_for(exc),
        content={"detail": exc.message},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
