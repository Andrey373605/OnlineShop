from typing import Callable, Awaitable
import logging
from fastapi import Request, Response

log = logging.getLogger(__name__)


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    log.info("Request %s %s", request.method, request.url.path)
    return await call_next(request)