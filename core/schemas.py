from pydantic import BaseModel, Field

from uuid import UUID
from datetime import date, datetime

from .utils.enums import GenderEnum


# we are storing all the main model of the feature
# to avoid circular imports because we share them all over the features
class GeneralResponseModel(BaseModel):
    message: str


class UserModel(BaseModel):
    uid: UUID
    full_name: str
    email: str
    gender: GenderEnum
    profile_url: str
    dob: date
    about: str
    username: str
    posts: list["PostModel"]
    following: list["UserModel"]
    followers: list["UserModel"]
    created_at: datetime
    updated_at: datetime


class TagModel(BaseModel):
    uid: UUID
    tag_name: str
    # posts: list["PostModel"] Exclude because of recursive serialization


class PostModel(BaseModel):
    uid: UUID
    caption: str
    tags: list["TagModel"]
    user_uid: UUID
    # user: "UserModel" = Field(exclude=True) because of recursive loop
    likes: list["LikeModel"]
    shares: list["ShareModel"]
    comments: list["CommentModel"]
    created_at: datetime
    updated_at: datetime


class ShareModel(BaseModel):
    uid: UUID
    sharer_uid: UUID


class CommentModel(BaseModel):
    comment: str
    commenter_uid: UUID
    commented_at: datetime
    # user: UserModel


class LikeModel(BaseModel):
    uid: UUID
    liker_uid: UUID
