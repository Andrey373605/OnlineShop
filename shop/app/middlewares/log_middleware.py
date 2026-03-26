import logging
import traceback
from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    # try:
    response = await call_next(request)
    # except Exception as exc:
    #     return await global_exception_handler(request, exc)
    try:
        service = request.app.state.event_log_service
        db_used = getattr(request.state, "used_db", False)
        await service.log_http_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            request=request,
            db_used=db_used,
        )
    except Exception as exc:
        log.exception("Failed to log request event: %s", exc)
    return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Логирует необработанные исключения приложения в MongoDB через
    EventLogService. HTTPException и RequestValidationError
    не перехватываются — их обрабатывает FastAPI.
    """
    try:
        service = request.app.state.event_log_service
        await service.log_error(
            description=str(exc),
            request=request,
            error_message=str(exc),
            stack_trace=traceback.format_exc(),
        )
    except Exception as log_exc:
        log.exception(log_exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

