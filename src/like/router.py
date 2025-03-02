from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Annotated

from core.database.main import get_session
from core.schemas import GeneralResponseModel
from src.auth.dependencies import access_token_bearer
from .service import like_service


like_router = APIRouter()


@like_router.post("/like-and-unlike-post", response_model=GeneralResponseModel)
async def add_like_to_post(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    post_uid: Annotated[str, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await like_service.like_and_unlike_post(user_data, post_uid, session)


# @like_router.get("/get-all-likers")
# async def get_all_likers_of_post():
#     pass
