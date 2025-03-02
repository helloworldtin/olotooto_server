from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from uuid import UUID

from core.database.models import Like
from core.exceptions.exceptions import InterServerException, InvalidOperation


class LikeService:
    async def get_like_by_liker_uid(
        self,
        liker_uid: UUID,
        session: AsyncSession,
    ):
        try:
            statement = select(Like).where(Like.liker_uid == liker_uid)
            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_like_by_uid(
        self,
        like_uid: UUID,
        session: AsyncSession,
    ) -> Like | None:
        try:
            statement = select(Like).where(Like.uid == like_uid)
            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def like_and_unlike_post(
        self,
        user_data: dict,
        post_uid: str,
        session: AsyncSession,
    ):
        try:
            liker_uid = UUID(user_data["user_data"]["uid"])
            already_liked_detail = await self.get_like_by_liker_uid(liker_uid, session)
            if already_liked_detail is not None:
                await session.delete(already_liked_detail)
                await session.commit()
                return {"message": "unlike the post"}
            new_like = Like(liker_uid=liker_uid, post_uid=post_uid)
            session.add(new_like)
            await session.commit()
            return {"message": "successfully liked the post"}

        except Exception as e:
            print(e)
            raise InterServerException()


like_service = LikeService()
