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
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User not found",
            },
        ),
    )
    app.add_exception_handler(
        UserAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "User with this email is already exist. Please login instead",
            },
        ),
    )
    app.add_exception_handler(
        UserNameAlreadyTaken,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "username is already taken by fellows, user other please",
            },
        ),
    )
    app.add_exception_handler(
        InvalidOTP,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid OTP code",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Invalid token get a new one please",
            },
        ),
    )
    app.add_exception_handler(
        ExpiredToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Expired token get a new one please",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Please check your credentials.",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Please provide access token.",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Please provide refresh token.",
            },
        ),
    )
    app.add_exception_handler(
        UnAuthenticated,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Not Authenticated please provide tokens.",
            },
        ),
    )
    app.add_exception_handler(
        AlreadyFollowed,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "You had already followed this user",
            },
        ),
    )
    app.add_exception_handler(
        InvalidOperation,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "This is not valid operation",
            },
        ),
    )
    app.add_exception_handler(
        TagAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "This tag is already exist don't need to create",
            },
        ),
    )
    app.add_exception_handler(
        PostNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Post not found",
            },
        ),
    )
