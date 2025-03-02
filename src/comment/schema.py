from pydantic import BaseModel

from uuid import UUID


class UpdatePostComment(BaseModel):
    post_uid: UUID
    comment: str
