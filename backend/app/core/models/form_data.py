from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.exceptions import InvalidInput
from app.core.types import FormLinkType, FormStatus
from app.util.logger import logger

from .base_model import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment
    from .form_template import FormTemplate
    from .request import Request
    from .track import Track
    from .user import User


class FormData(BaseModel):
    __tablename__ = "form_data"

    __payload: Mapped[dict | None] = mapped_column("payload", JSON, nullable=True)
    payload_unvalidated: Mapped[dict | None] = mapped_column("payload_unvalidated", JSON, nullable=True)

    form_template_id: Mapped[UUID] = mapped_column(ForeignKey("form_template.id", ondelete="CASCADE"), nullable=False)

    form_template: Mapped[FormTemplate] = relationship("FormTemplate", lazy="joined")

    track_id: Mapped[UUID | None] = mapped_column(ForeignKey("track.id", ondelete="CASCADE"), nullable=True)
    track: Mapped[Track | None] = relationship("Track", back_populates="forms")

    appointment_id: Mapped[UUID | None] = mapped_column(ForeignKey("appointment.id", ondelete="CASCADE"), nullable=True)
    appointment: Mapped[Appointment | None] = relationship("Appointment", back_populates="forms")

    request_id: Mapped[UUID | None] = mapped_column(ForeignKey("request.id", ondelete="CASCADE"), nullable=True)
    request: Mapped[Request | None] = relationship("Request", back_populates="forms")

    last_updated_by_user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    last_updated_by_user: Mapped[User | None] = relationship("User", lazy="joined")

    completed: Mapped[bool] = mapped_column("completed", nullable=False, server_default="false")

    submitted: Mapped[bool] = mapped_column("submitted", nullable=False, server_default="false")
    submitted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=func.now(),
        server_default=func.now(),
    )

    approved: Mapped[bool] = mapped_column("approved", nullable=False, server_default="false")
    approved_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=func.now(),
        server_default=func.now(),
    )

    @property
    def approval_required(self):
        if self.last_updated_by_user:
            return self.last_updated_by_user.has_role("partner") or self.last_updated_by_user.has_role("ondernemer")
        else:
            return True

    @property
    def payload(self):
        return self.__payload

    @property
    def has_valid_payload(self):
        return self.payload is not None

    def get_payload_validation(self, payload: dict):
        # Validate payload against the form template
        validation = self.form_template.get_payload_validation(payload)
        return validation

    @payload.setter
    def payload(self, value: dict | None):
        if value is not None:
            validation = self.get_payload_validation(value)
            if len(validation.errors) > 0:
                logger.error(f"Invalid payload for form data {self.id}: {validation.errors}")
                raise InvalidInput(f"Invalid payload: {validation.errors}")

        self.__payload = value

    @property
    def form_template_name(self):
        return self.form_template.name

    @property
    def status(self):
        if self.approved:
            return FormStatus.APPROVED
        elif self.submitted:
            return FormStatus.SUBMITTED
        else:
            return FormStatus.INITIALIZED

    @property
    def form_link_type(self) -> FormLinkType | None:
        if self.appointment_id is not None:
            return "appointment"
        elif self.request_id is not None:
            return "request"
        elif self.track_id is not None:
            return "track"
        else:
            return None

    @property
    def case_id(self):
        return self.case.id if self.case else None

    @property
    def case(self):
        if self.appointment:
            return self.appointment.case
        elif self.request:
            return self.request.case
        elif self.track:
            return self.track.case
        else:
            return None

    @property
    def case_description(self):
        if self.case:
            return self.case.description
