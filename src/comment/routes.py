from fastapi import APIRouter, Depends, Body, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Annotated

from core.database.main import get_session
from core.schemas import GeneralResponseModel
from src.auth.dependencies import access_token_bearer
from .service import comment_service
from .schema import UpdatePostComment

comment_router = APIRouter()


@comment_router.post(
    "/add-comment",
    status_code=201,
    response_model=GeneralResponseModel,
)
async def add_comment(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    comment_data: Annotated[UpdatePostComment, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await comment_service.add_comment_to_post(
        user_data,
        comment_data,
        session,
    )


@comment_router.patch(
    "/update-comment/{comment_uid}",
    response_model=GeneralResponseModel,
)
async def update_comment(
    _: Annotated[dict, Depends(access_token_bearer)],
    comment_uid: Annotated[str, Path()],
    new_comment: Annotated[str, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await comment_service.update_comment(new_comment, comment_uid, session)


@comment_router.delete("/delete-comment/{comment_uid}", status_code=204)
async def update_comment(
    _: Annotated[dict, Depends(access_token_bearer)],
    comment_uid: Annotated[str, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    await comment_service.delete_comment(comment_uid, session)
