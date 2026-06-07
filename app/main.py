from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter
from app.api.v1.router import router
from app.core.exceptions import (
    BadRequest,
    Conflict,
    DetailedHTTPException,
    NotFound,
    exception_handler,
)
from app.core.config import settings


app = FastAPI()


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_exception_handler(DetailedHTTPException, exception_handler)
app.add_exception_handler(NotFound, exception_handler)
app.add_exception_handler(Conflict, exception_handler)
app.add_exception_handler(BadRequest, exception_handler)


app.include_router(router)
