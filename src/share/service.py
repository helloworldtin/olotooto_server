from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from uuid import UUID

from core.database.models import Share
from core.exceptions.exceptions import InterServerException, InvalidOperation


class ShareService:
    async def get_share_detail_by_uid(self, share_uid: UUID, session: AsyncSession):
        try:
            statement = select(Share).where(Share.uid == share_uid)
            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_share_by_sharer_uid(self, sharer_uid: UUID, session: AsyncSession):
        try:
            statement = select(Share).where(Share.sharer_uid == sharer_uid)
            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def share_the_post(
        self, user_data: dict, post_uid: UUID, session: AsyncSession
    ):
        try:
            sharer_uid = UUID(user_data["user_data"]["uid"])
            already_shared = await self.get_share_by_sharer_uid(sharer_uid, session)
            if already_shared is not None:
                raise InvalidOperation()
            new_share_detail = Share(sharer_uid=sharer_uid, post_uid=post_uid)
            session.add(new_share_detail)
            await session.commit()
            return {
                "message": "post shared successfully",
            }
        except InvalidOperation:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_user_shared_post(self, user_data: dict, session: AsyncSession):

        try:
            sharer_uid = user_data["user_data"]["uid"]
            statement = select(Share).where(Share.sharer_uid == sharer_uid)
            result = await session.exec(statement)
            return result.all()

        except Exception as e:
            print(e)
            raise InterServerException()

    async def delete_share(self, share_uid: UUID, session: AsyncSession):
        try:
            share_detail = await self.get_share_detail_by_uid(share_uid, session)
            if share_detail is None:
                raise InvalidOperation()
            await session.delete(share_detail)
            await session.commit()
        except InvalidOperation:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()


share_service = ShareService()
