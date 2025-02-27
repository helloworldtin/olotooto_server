from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.requests import Request

from .utils import decode_jwt_token
from src.exceptions.exceptions import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    UnAuthenticated,
)


class JWTTokenBearer(HTTPBearer):
    def __init__(self, auto_error=False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:

        creds = await super().__call__(request)
        if creds is None:
            raise UnAuthenticated()
        token = creds.credentials

        token_data = decode_jwt_token(token=token)

        if token_data is None:
            raise InvalidToken()

        self.verify_token_data(token_data)
        return token_data

    def verify_token_data(self, _: dict):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(JWTTokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(JWTTokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
