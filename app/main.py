from fastapi import FastAPI

from app.api.v1.router import router
from app.core.exceptions import (
    BadRequest,
    Conflict,
    DetailedHTTPException,
    NotFound,
    exception_handler,
)

app = FastAPI()

app.add_exception_handler(DetailedHTTPException, exception_handler)
app.add_exception_handler(NotFound, exception_handler)
app.add_exception_handler(Conflict, exception_handler)
app.add_exception_handler(BadRequest, exception_handler)


app.include_router(router)
