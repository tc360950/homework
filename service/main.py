import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from service.controllers import router

logger = logging.getLogger(__name__)


app = FastAPI()
app.include_router(router)


@app.exception_handler(ValueError)
def value_error_exception_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )
