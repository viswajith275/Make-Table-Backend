from fastapi import FastAPI
from app.core.exceptions import DetailedHTTPException, NotFound, BadRequest, Conflict, exception_handler
from app.api.v1.router import router

app = FastAPI()

app.add_exception_handler(DetailedHTTPException, exception_handler)
app.add_exception_handler(NotFound, exception_handler)
app.add_exception_handler(Conflict, exception_handler)
app.add_exception_handler(BadRequest, exception_handler)



app.include_router(router)