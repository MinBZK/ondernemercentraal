from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment
    from .case import Case
    from .comment import Comment
    from .track import Track
from sqlalchemy import UniqueConstraint


class CommentThread(BaseModel):
    __tablename__ = "comment_thread"

    track_id: Mapped[UUID | None] = mapped_column(ForeignKey("track.id", ondelete="CASCADE"), nullable=True)
    track: Mapped[Track | None] = relationship("Track")

    case_id: Mapped[UUID | None] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"), nullable=True)
    case: Mapped[Case | None] = relationship("Case")

    appointment_id: Mapped[UUID | None] = mapped_column(ForeignKey("appointment.id", ondelete="CASCADE"), nullable=True)
    appointment: Mapped[Appointment | None] = relationship("Appointment")

    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="comment_thread", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("case_id", "appointment_id", "track_id", name="uq_appointment_track_case"),)
