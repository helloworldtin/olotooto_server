from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Annotated
from uuid import UUID

from core.database.main import get_session
from core.schemas import GeneralResponseModel
from src.auth.dependencies import access_token_bearer
from .service import share_service


share_router = APIRouter()


@share_router.post("/share-post", status_code=201, response_model=GeneralResponseModel)
async def share_post(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    post_uid: Annotated[UUID, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await share_service.share_the_post(user_data, post_uid, session)


@share_router.delete("/delete-share", status_code=204)
async def share_post(
    _: Annotated[dict, Depends(access_token_bearer)],
    share_uid: Annotated[UUID, Query()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await share_service.delete_share(share_uid, session)


@share_router.get("/get-user-shared-posts")
async def get_user_shared_post(
    user_data: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await share_service.get_user_shared_post(user_data, session)
