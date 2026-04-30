from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from shop.app.core.exceptions import (
    AppError,
)


def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
