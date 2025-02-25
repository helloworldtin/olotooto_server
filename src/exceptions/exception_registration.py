from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from typing import Callable

from .exceptions import *


def create_exception_handler(
    status_code: int,
    detail: dict,
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=status_code, content=detail)

    return exception_handler


def register_exception_handlers(app: FastAPI) -> None:
    # This is for the status code of 500
    app.add_exception_handler(
        500,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"},
        ),
    )

    # These all are for the class based Exceptions
    app.add_exception_handler(
        InterServerException,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Internal server error",
            },
        ),
    )
