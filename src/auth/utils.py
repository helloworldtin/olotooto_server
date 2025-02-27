from argon2 import PasswordHasher
import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError

import random
from datetime import datetime, timedelta, timezone

from src.exceptions.exceptions import InterServerException, InvalidToken, ExpiredToken
from src.config import Config


argon = PasswordHasher()


def generate_otp() -> str:
    """generate the otp of length of 6"""
    otp = ""
    for _ in range(6):
        otp += str(random.randint(0, 9))
    return otp


def hash_password(password: str) -> str:
    try:
        return argon.hash(password=password)
    except Exception as e:
        print(f"error while hashing password: {e}")
        raise InterServerException()


def verify_hashed_password(password: str, hashed_password: str) -> bool:
    try:
        return argon.verify(password=password, hash=hashed_password)
    except Exception:
        return False


def create_jwt_token(
    data: dict,
    exp_time: timedelta = timedelta(days=1),
    refresh: bool = False,
) -> str:
    try:
        payload = {
            "user_data": data,
            "exp": datetime.now(timezone.utc) + exp_time,
            "refresh": refresh,
        }
        token = jwt.encode(
            payload=payload,
            key=Config.JWT_SECRETE,
            algorithm=Config.JWT_ALGO,
        )
        return token
    except Exception as e:
        print(e)
        raise InterServerException()


def decode_jwt_token(token: str) -> dict:
    try:
        data: dict = jwt.decode(
            token,
            algorithms=[Config.JWT_ALGO],
            key=Config.JWT_SECRETE,
            options={"verify_exp": True},
        )
        return data
    except ExpiredSignatureError:
        raise ExpiredToken()
    except PyJWTError as e:
        print(e)
        raise InvalidToken()
    except Exception as e:
        print(e)
        raise InterServerException()
