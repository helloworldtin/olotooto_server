from fastapi import (
    APIRouter,
    UploadFile,
    BackgroundTasks,
    Depends,
    Form,
    File,
    Body,
    Query,
    Path,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr

from datetime import date
from typing import Annotated

from .schemas import (
    UserModel,
    CreteUserModel,
    VerifyOTPDataModel,
    LoginAndTokensResponseModel,
    LoginDataModel,
    ChangePasswordModel,
    UpdateDataModel,
    UpdatePasswordModel,
    UserModelWithLists,
)
from .controller import auth_controller
from .dependencies import refresh_token_bearer, access_token_bearer
from src.database.main import get_session
from src.utils.enums import GenderEnum
from src.utils.schemas import GeneralResponseModel

auth_router = APIRouter()


@auth_router.post("/register", status_code=201, response_model=UserModel)
async def create_user(
    full_name: Annotated[str, Form()],
    email: Annotated[EmailStr, Form()],
    gender: Annotated[GenderEnum, Form()],
    about: Annotated[str, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    profile_file: Annotated[UploadFile, File()],
    dob: Annotated[date, Form()],
    background_task: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    user_data = CreteUserModel(
        full_name=full_name,
        email=email,
        gender=gender,
        about=about,
        username=username,
        password=password,
        profile_file=profile_file,
        dob=dob,
    )
    return await auth_controller.create_user(
        user_data=user_data,
        session=session,
        background_task=background_task,
    )


@auth_router.post("/verify-opt", response_model=GeneralResponseModel)
async def verify_opt(
    verify_opt_data: Annotated[VerifyOTPDataModel, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.verify_otp(verify_opt_data, session)


@auth_router.post("/login", response_model=LoginAndTokensResponseModel)
async def login(
    login_data: Annotated[LoginDataModel, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.login(login_data, session)


@auth_router.get("/send-password-forgot-request", response_model=GeneralResponseModel)
async def send_password_forgot_request(
    email: Annotated[EmailStr, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
    background_task: BackgroundTasks,
):
    return await auth_controller.send_password_forgot_request(
        email, session, background_task
    )


@auth_router.post("/change-password-forgot", response_model=UserModel)
async def change_password_forgot(
    password_change_data: Annotated[ChangePasswordModel, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.change_password_forgot(password_change_data, session)


@auth_router.get("/get-new-tokens", response_model=LoginAndTokensResponseModel)
async def get_new_tokens(
    user_data: Annotated[dict, Depends(refresh_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    print(user_data)
    return await auth_controller.get_new_tokens(user_data, session)


@auth_router.patch("/update-profile", response_model=UserModel)
async def get_new_tokens(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    new_profile_file: Annotated[UploadFile, File()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.update_profile(
        new_profile_file=new_profile_file,
        user_data=user_data,
        session=session,
    )


@auth_router.patch("/update-user-data", response_model=UserModel)
async def update_data(
    update_data: Annotated[UpdateDataModel, Body()],
    user_data: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.update_user_data(update_data, user_data, session)


@auth_router.patch("/update-password", response_model=GeneralResponseModel)
async def update_password(
    update_password_data: Annotated[UpdatePasswordModel, Body()],
    user_data: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.update_password(
        update_password_data, user_data, session
    )


@auth_router.get("/search-users", response_model=list[UserModel])
async def search_users(
    search_key: Annotated[str, Query()],
    _: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.search_users(search_key, session)


@auth_router.get("/current-user", response_model=UserModelWithLists)
async def get_current_user(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.get_current_user(user_data, session)


@auth_router.get("/follow-user", response_model=GeneralResponseModel)
async def follow_user(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    following_username: Annotated[str, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.follow_user(user_data, following_username, session)


@auth_router.get(
    "/unfollow-user/{un_flowing_username}", response_model=GeneralResponseModel
)
async def unfollow_user(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    un_flowing_username: Annotated[str, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await auth_controller.unfollow_user(user_data, un_flowing_username, session)


@auth_router.delete("/delete-user", status_code=204)
async def delete_user(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    await auth_controller.delete_user(user_data, session)
