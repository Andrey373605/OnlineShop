from fastapi import FastAPI

from shop.app.middlewares.log_middleware import log_requests


def register_middleware(app: FastAPI):
    app.middleware("http")(log_requests)