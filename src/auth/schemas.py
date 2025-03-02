from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from core.utils.enums import GenderEnum

from datetime import date


class CreteUserModel(BaseModel):
    full_name: str
    email: EmailStr
    gender: GenderEnum
    about: str
    username: str
    password: str
    profile_file: UploadFile
    dob: date


class VerifyOTPDataModel(BaseModel):
    email: EmailStr
    otp: str


class LoginDataModel(BaseModel):
    email: EmailStr
    password: str


class LoginAndTokensResponseModel(BaseModel):
    message: str
    access_token: str
    refresh_token: str


class ChangePasswordModel(BaseModel):
    email: EmailStr
    new_password: str


class UpdateDataModel(BaseModel):
    full_name: str | None = None
    gender: GenderEnum | None = None
    about: str | None = None
    username: str | None = None
    old_password: str | None = None
    new_password: str | None = None


class UpdatePasswordModel(BaseModel):
    old_password: str
    new_password: str
