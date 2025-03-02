from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from uuid import UUID
from datetime import datetime

from .schemas import PostCreateModel, PostUpdateModel
from core.database.models import Post, User
from core.database.cloudinary import upload_file, delete_file
from src.auth.service import auth_service
from src.tag.service import tag_service
from core.exceptions.exceptions import (
    InterServerException,
    UserNotFound,
    PostNotFound,
    TagAlreadyExist,
)
from core.database.cloudinary import upload_file


def get_post_path(full_name: str):
    return f"users/{full_name}/posts"


class PostService:
    async def get_post_by_uid(
        self, post_uid: UUID, session: AsyncSession
    ) -> Post | None:
        try:
            statement = select(Post).where(Post.uid == post_uid)
            result = await session.exec(statement)
            return result.first()

        except Exception as e:
            print(e)
            raise InterServerException()

    async def upload_post(
        self,
        user_data: dict,
        post_create_data: PostCreateModel,
        session: AsyncSession,
    ):
        try:
            user: User | None = await auth_service.get_user_by_username(
                user_data["user_data"]["username"], session
            )
            if user is None:
                raise UserNotFound()
            post_image_url = await upload_file(
                post_create_data.post_image_file,
                get_post_path(user.full_name),
            )
            new_post = Post(
                caption=post_create_data.caption,
                post_image_url=post_image_url,
                user_uid=user.uid,
            )
            session.add(new_post)
            await session.commit()
            await session.refresh(new_post)
            if len(post_create_data.tags) > 0:
                for tag in post_create_data.tags:

                    await tag_service.add_tag_to_post(new_post.uid, tag, session)

            return {"message": "Post created successfully"}
        except (UserNotFound, TagAlreadyExist):
            raise

        except Exception as e:
            print(e)
            raise InterServerException()

    async def update_post(
        self, post_uid: str, post_update_data: PostUpdateModel, session: AsyncSession
    ):
        try:
            post = await self.get_post_by_uid(UUID(post_uid), session)
            if not post:
                raise PostNotFound()
            for k, v in post_update_data.model_dump().items():
                if v == None:
                    continue
                if k == "post_image_file":
                    post_folder_path = get_post_path(post.user.full_name)
                    await delete_file(
                        post.post_image_url,
                        post_folder_path,
                    )
                    new_profile_url = await upload_file(
                        post_update_data.post_image_file,
                        post_folder_path,
                    )
                    post.post_image_url = new_profile_url
                elif k == "tags":
                    post.tags.clear()
                    if len(post_update_data.tags) > 0:
                        for tag in post_update_data.tags:
                            await tag_service.add_tag_to_post(post.uid, tag, session)
                else:
                    post.caption = post_update_data.caption
            post.updated_at = datetime.now()
            await session.commit()
            return {
                "message": "Post updated successfully",
            }
        except PostNotFound:
            raise

        except Exception as e:
            print(e)
            raise InterServerException()

    async def delete_post(self, post_uid: str, session: AsyncSession) -> None:
        try:
            post = await self.get_post_by_uid(UUID(post_uid), session)
            if post is None:
                raise PostNotFound()
            await session.delete(post)
            await session.commit()
        except PostNotFound:
            raise
        except Exception as e:
            print(e)
            raise InterServerException()


post_service = PostService()
