from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from typing import Annotated

from core.database.main import get_session
from core.schemas import PostModel
from src.auth.dependencies import access_token_bearer
from .service import tag_service

tag_router = APIRouter()


@tag_router.get("/get-all-posts-by-tag")
async def create_tag(
    tag_name: Annotated[str, Query()],
    _: Annotated[dict, Depends(access_token_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await tag_service.get_posts_by_tag(tag_name, session)
