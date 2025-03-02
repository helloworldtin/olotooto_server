from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload

from uuid import UUID

from core.database.models import Tag, Post, TagAndPostLinkModel
from core.exceptions.exceptions import (
    TagAlreadyExist,
    InterServerException,
    PostNotFound,
)


class TagService:
    async def get_tag_by_name(self, tag_name: str, session: AsyncSession) -> Tag | None:
        try:
            statement = (
                select(Tag)
                .options(selectinload(Tag.posts))
                .where(Tag.tag_name == tag_name)
            )

            result = await session.exec(statement)
            return result.first()
        except Exception as e:
            print(e)
            raise InterServerException()

    async def create_tag(self, tag_name: str, session: AsyncSession):
        try:
            is_tag_in_db = await self.get_tag_by_name(tag_name, session)
            if is_tag_in_db:
                raise TagAlreadyExist()
            new_tag = Tag(tag_name=tag_name)
            session.add(new_tag)
            await session.commit()
            return new_tag
        except TagAlreadyExist:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def add_tag_to_post(
        self,
        post_uid: UUID,
        tag_name: str,
        session: AsyncSession,
    ) -> dict:
        try:
            from src.post.service import post_service

            post: Post | None = await post_service.get_post_by_uid(post_uid, session)
            if post is None:
                raise PostNotFound()
            tag_name = tag_name.strip().lower()
            if not tag_name.startswith("#"):
                tag_name = "#" + tag_name
            tag: Tag | None = await self.get_tag_by_name(tag_name, session)

            if tag is None:
                new_tag = await self.create_tag(tag_name, session)
                link_entry = TagAndPostLinkModel(tag_uid=new_tag.uid, post_uid=post.uid)
                session.add(link_entry)
                # await session.refresh(link_entry)
            else:
                existing_link = await session.exec(
                    select(TagAndPostLinkModel).where(
                        TagAndPostLinkModel.post_uid == post.uid,
                        TagAndPostLinkModel.tag_uid == tag.uid,
                    )
                )
                if not existing_link.first():
                    link_entry = TagAndPostLinkModel(post_uid=post.uid, tag_uid=tag.uid)
                    session.add(link_entry)
                    # await session.refresh(link_entry)

            await session.commit()
            return {"message": "Tag added successfully"}

        except (PostNotFound, TagAlreadyExist):
            raise
        except Exception as e:
            print(e)
            raise InterServerException()

    async def get_posts_by_tag(self, tag_name, session):
        try:
            tag: Tag | None = await self.get_tag_by_name(tag_name, session)
            if tag is None:
                return []
            return tag.posts

        except Exception as e:
            print(e)
            raise InterServerException()


tag_service = TagService()
