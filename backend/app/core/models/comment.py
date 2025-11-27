from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .comment_thread import CommentThread
    from .user import User


class Comment(BaseModel):
    __tablename__ = "comment"

    content: Mapped[str | None] = mapped_column(VARCHAR(2048), nullable=True, unique=False)

    created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created_by_user: Mapped[User] = relationship("User", lazy="joined", foreign_keys=[created_by_user_id])

    comment_thread_id: Mapped[UUID] = mapped_column(ForeignKey("comment_thread.id", ondelete="CASCADE"), nullable=False)
    comment_thread: Mapped[CommentThread] = relationship("CommentThread", lazy="joined")
