from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from uuid import UUID
from datetime import datetime

from core.exceptions.exceptions import (
    InterServerException,
    PostNotFound,
    InvalidOperation,
)
from core.database.models import Comment
from src.post.service import post_service
from .schema import UpdatePostComment


class CommentService:
    async def get_comment_by_uid(self, comment_uid: UUID, session: AsyncSession):
        try:
            statement = select(Comment).where(Comment.comment_uid == comment_uid)
            result = await session.exec(statement)
            return result.first()

        except Exception as e:
            print(e)
            raise InterServerException()

    async def add_comment_to_post(
        self,
        user_data: dict,
        comment_data: UpdatePostComment,
        session: AsyncSession,
    ):
        try:
            post = await post_service.get_post_by_uid(
                comment_data.post_uid, session=session
            )
            commenter_uid = user_data["user_data"]["uid"]
            if post is None:
                raise PostNotFound()
            comment = Comment(
                post_uid=comment_data.post_uid,
                commenter_uid=UUID(commenter_uid),
                comment=comment_data.comment,
            )
            session.add(comment)
            await session.commit()
            return {
                "message": "Comment added successfully",
            }
        except PostNotFound:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def update_comment(
        self,
        new_comment: str,
        comment_uid: str,
        session: AsyncSession,
    ):
        try:
            comment: Comment | None = await self.get_comment_by_uid(
                UUID(comment_uid), session
            )
            if comment is None:
                raise InvalidOperation()
            if new_comment.strip() == comment.comment.strip():
                raise InvalidOperation()
            comment.comment = new_comment
            comment.updated_at = datetime.now()
            await session.commit()
            await session.refresh(comment)
            return {
                "message": "comment updated successfully",
            }
        except InvalidOperation:
            raise

        except Exception as e:
            print(e)
            raise InterServerException()

    async def delete_comment(self, comment_uid: str, session: AsyncSession):

        try:
            comment = await self.get_comment_by_uid(UUID(comment_uid), session)
            if not comment:
                raise InvalidOperation()
            await session.delete(comment)
            await session.commit()
        except InterServerException:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()


comment_service = CommentService()
