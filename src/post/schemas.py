from pydantic import BaseModel
from fastapi import UploadFile

from datetime import datetime
from uuid import UUID


class PostCreateModel(BaseModel):
    caption: str
    tags: list[str] | None = None
    post_image_file: UploadFile


class PostUpdateModel(BaseModel):
    caption: str | None = None
    tags: list[str] | None = None
    post_image_file: UploadFile | None = None
