import logging
import traceback
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from shop.app.core.state import get_app_state
from shop.app.repositories.event_log_mongo_repository import EventLogRepositoryMongo
from shop.app.services.event_log_service import EventLogService

log = logging.getLogger(__name__)


def _get_event_log_service(request: Request) -> EventLogService:
    db = get_app_state(request).mongo_db
    return EventLogService(repo=EventLogRepositoryMongo(db=db))


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response = await call_next(request)
    try:
        service = _get_event_log_service(request)
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
        service = _get_event_log_service(request)
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

