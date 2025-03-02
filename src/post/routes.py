from fastapi import APIRouter, UploadFile, Body, File, Form, Path, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Annotated

from core.database.main import get_session
from core.schemas import PostModel, GeneralResponseModel
from src.auth.dependencies import access_token_bearer
from .schemas import PostCreateModel, PostUpdateModel
from .service import post_service


post_router = APIRouter()


@post_router.post(
    "/upload-post",
    response_model=GeneralResponseModel,
    status_code=201,
)
async def upload_post(
    caption: Annotated[str, Form()],
    tags: Annotated[list[str], Form()],
    post_image_file: Annotated[UploadFile, File()],
    user_data: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    post_data = PostCreateModel(
        caption=caption,
        post_image_file=post_image_file,
        tags=tags,
    )
    return await post_service.upload_post(
        user_data=user_data,
        post_create_data=post_data,
        session=session,
    )


@post_router.get("/{post_uid}", response_model=PostModel)
async def get_post_by_uid(
    post_uid: Annotated[str, Path()],
    _: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await post_service.get_post_by_uid(post_uid, session)


@post_router.patch("/update-post/{post_uid}")
async def update_post(
    caption: Annotated[str, Form()],
    tags: Annotated[list[str], Form()],
    post_image_file: Annotated[UploadFile, File()],
    post_uid: Annotated[str, Path()],
    _: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    post_update_data = PostUpdateModel(
        caption=caption, tags=tags, post_image_file=post_image_file
    )
    return await post_service.update_post(post_uid, post_update_data, session)


@post_router.delete("/delete-post/{post_uid}", status_code=204)
async def delete_post(
    post_uid: Annotated[str, Path()],
    _: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    await post_service.delete_post(post_uid, session)
