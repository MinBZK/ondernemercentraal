from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import VARCHAR, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.types import FileType

from .base_model import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment
    from .case import Case
    from .track import Track
    from .user import User
from sqlalchemy import UniqueConstraint


class File(BaseModel):
    __tablename__ = "file"

    file_type: Mapped[FileType] = mapped_column(VARCHAR(256), nullable=False, unique=False)

    description: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True, unique=False)
    filename: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=False)
    object_id: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)

    track_id: Mapped[UUID | None] = mapped_column(ForeignKey("track.id", ondelete="CASCADE"), nullable=True)
    track: Mapped[Track | None] = relationship("Track")

    case_id: Mapped[UUID | None] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"), nullable=True)
    case: Mapped[Case | None] = relationship("Case")

    appointment_id: Mapped[UUID | None] = mapped_column(ForeignKey("appointment.id", ondelete="CASCADE"), nullable=True)
    appointment: Mapped[Appointment | None] = relationship("Appointment")

    uploaded_by_user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    uploaded_by_user: Mapped[User] = relationship("User", lazy="joined", foreign_keys=[uploaded_by_user_id])

    approved_by_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    approved_by_user: Mapped[User | None] = relationship("User", lazy="joined", foreign_keys=[approved_by_user_id])
    approved: Mapped[bool] = mapped_column("approved", nullable=False, server_default="false")
    approved_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=func.now(),
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("case_id", "filename", name="uq_case_filename"),
        UniqueConstraint("track_id", "filename", name="uq_track_filename"),
        UniqueConstraint("appointment_id", "filename", name="uq_appointment_filename"),
    )

    @property
    def approval_required(self):
        return self.file_type in ["Plan van aanpak"]
