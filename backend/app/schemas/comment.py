from uuid import UUID

from .base import BaseSchema
from .user import UserBase


class Comment(BaseSchema):
    content: str
    created_by_user: UserBase
    comment_thread_id: UUID
