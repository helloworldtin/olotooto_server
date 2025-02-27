from sqlmodel import (
    SQLModel,
    UUID,
    Column,
    Enum,
    ForeignKey,
    TIMESTAMP,
    Date,
    String,
    Field,
    Relationship,
)


import uuid
import datetime

from src.utils.enums import GenderEnum

# for users


class UserLinkModel(SQLModel, table=True):
    __tablename__ = "userlinks"
    follower_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("users.uid"),
            primary_key=True,
        )
    )  # the person who follow someone
    user_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("users.uid"),
            primary_key=True,
        )
    )  # the person who is followed


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    full_name: str = Field(nullable=False)
    email: str = Field(nullable=False)
    gender: GenderEnum = Field(
        sa_column=Column(
            Enum(GenderEnum),
            nullable=False,
            index=True,
        )
    )
    profile_url: str = Field(
        sa_column=Column(
            String,
            server_default="https://img.freepik.com/free-psd/contact-icon-illustration-isolated_23-2151903337.jpg?t=st=1740481711~exp=1740485311~hmac=de8146f0bcc8630a725995aeed260b912e5d81f35024e30d7980cd861c0a693b&w=1480",
        )
    )
    dob: datetime.date = Field(
        sa_column=Column(
            Date,
            nullable=False,
        )
    )
    about: str = Field(nullable=False)
    username: str = Field(nullable=False, unique=True)
    hashed_password: str = Field(nullable=False, exclude=True)

    posts: list["Post"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
        },
    )
    following: list["User"] = Relationship(
        link_model=UserLinkModel,
        back_populates="followers",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "primaryjoin": "and_(User.uid == foreign(UserLinkModel.follower_uid), User.uid != UserLinkModel.user_uid)",
            "secondaryjoin": "User.uid == foreign(UserLinkModel.user_uid)",
        },
    )

    followers: list["User"] = Relationship(
        link_model=UserLinkModel,
        back_populates="following",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "primaryjoin": "and_(User.uid == foreign(UserLinkModel.user_uid), User.uid != UserLinkModel.follower_uid)",
            "secondaryjoin": "User.uid == foreign(UserLinkModel.follower_uid)",
        },
    )

    created_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            default=datetime.datetime.now,
        )
    )
    updated_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            default=datetime.datetime.now,
        )
    )


class TagAndPostLinkModel(SQLModel, table=True):
    __tablename__ = "tagpostlinks"
    tag_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("tags.uid"),
            primary_key=True,
        )
    )

    post_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("posts.uid"),
            primary_key=True,
        )
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    tag_name: str = Field(nullable=False)
    posts: list["Post"] = Relationship(
        back_populates="tags",
        link_model=TagAndPostLinkModel,
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class Comment(SQLModel, table=True):
    __tablename__ = "comments"
    comment_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    post_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("posts.uid"),
        )
    )
    post: "Post" = Relationship(
        back_populates="comments",
    )

    commenter_uid: uuid.UUID = Field(Column(UUID, ForeignKey("users.uid")))
    comment: str = Field(nullable=False)
    commented_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            default=datetime.datetime.now,
        )
    )
    updated_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            default=datetime.datetime.now,
        )
    )


class Like(SQLModel, table=True):
    __tablename__ = "likes"
    uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    liker_uid: uuid.UUID = Field(Column(UUID, ForeignKey("users.uid")))
    post_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("posts.uid"),
        )
    )
    post: "Post" = Relationship(back_populates="likes")


class Share(SQLModel, table=True):
    __tablename__ = "shares"
    uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,
        )
    )
    sharer_uid: uuid.UUID = Field(Column(UUID, ForeignKey("users.uid")))
    post_uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("posts.uid"),
        )
    )
    post: "Post" = Relationship(back_populates="shares")


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    uid: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            primary_key=True,
            default=uuid.uuid4,
        ),
    )
    caption: str = Field(nullable=False)
    tags: list["Tag"] = Relationship(
        back_populates="posts",
        link_model=TagAndPostLinkModel,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    user_uid: uuid.UUID = Field(
        sa_column=Column(UUID, ForeignKey("users.uid"), nullable=False)
    )
    user: "User" = Relationship(
        back_populates="posts",
    )
    comments: list["Comment"] = Relationship(
        cascade_delete=True,
        back_populates="post",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    likes: list["Like"] = Relationship(
        cascade_delete=True,
        back_populates="post",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    shares: list["Share"] = Relationship(
        cascade_delete=True,
        back_populates="post",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    created_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            default=datetime.datetime.now,
        )
    )
    updated_at: datetime.datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            default=datetime.datetime.now,
        )
    )
