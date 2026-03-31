from fastapi import FastAPI

from shop.app.middlewares.log_middleware import global_exception_handler, log_requests


def setup_middleware(app: FastAPI) -> None:
    app.middleware("http")(log_requests)
    app.add_exception_handler(Exception, global_exception_handler)