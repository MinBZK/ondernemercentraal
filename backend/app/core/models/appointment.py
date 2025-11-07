from __future__ import annotations

import datetime as dt
import locale
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from sqlalchemy import UUID, VARCHAR, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.types import AppointmentStatus, AppointmentTypeName, FormNames
from app.schemas.form_template import RequiredFormTemplate

from .base_model import BaseModel

if TYPE_CHECKING:
    from .appointment_type import AppointmentType
    from .case import Case
    from .form_data import FormData
    from .partner_organization import PartnerOrganization
    from .track import Track


class Appointment(BaseModel):
    __tablename__ = "appointment"

    start_time: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, unique=False)
    end_time: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, unique=False)
    case_id: Mapped[UUID] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"), nullable=False)

    case: Mapped[Case] = relationship(
        "Case",
        back_populates="appointments",
    )

    appointment_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("appointment_type.id", ondelete="CASCADE"), nullable=False
    )

    appointment_type: Mapped[AppointmentType] = relationship("AppointmentType", lazy="joined")

    partner_organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("partner_organization.id", ondelete="CASCADE"), nullable=True
    )
    _partner_organization: Mapped[PartnerOrganization | None] = relationship(
        "PartnerOrganization", back_populates="appointments", lazy="joined"
    )

    track_id: Mapped[UUID | None] = mapped_column(ForeignKey("track.id", ondelete="CASCADE"), nullable=True)
    track: Mapped[Track | None] = relationship("Track", back_populates="appointments")

    status: Mapped[AppointmentStatus] = mapped_column(VARCHAR(256), nullable=False, unique=False)

    forms: Mapped[list[FormData]] = relationship("FormData", back_populates="appointment", cascade="all, delete-orphan")

    @property
    def partner_organization(self):
        """Return the partner organization associated with this appointment."""
        if self.track and self.track.partner_organization:
            return self.track.partner_organization
        else:
            return self._partner_organization

    @partner_organization.setter
    def partner_organization(self, value: PartnerOrganization | None):
        self._partner_organization = value

    @property
    def partner_organization_name(self):
        if self.partner_organization:
            return self.partner_organization.name

    def get_formatted_appointment_slot(self):
        start_time = self.start_time
        end_time = self.end_time
        assert start_time is not None and end_time is not None, "Appointment must have start and end time"
        locale.setlocale(locale.LC_TIME, "nl_NL.UTF-8")
        start_time_local = start_time.astimezone(ZoneInfo("Europe/Amsterdam"))
        end_time_local = end_time.astimezone(ZoneInfo("Europe/Amsterdam"))
        start_date_str = start_time_local.strftime("%A %-d %B")
        start_time_str = start_time_local.strftime("%H:%M")
        end_time_str = end_time_local.strftime("%H:%M")
        return f"{start_date_str} {start_time_str} u - {end_time_str} u"

    def get_confirmation_mail_content(self):
        content = [
            "Hierbij bevestigen wij uw afspraak.",
            "Uw afspraak:",
            f"{self.appointment_type.name}<br />{self.get_formatted_appointment_slot()}",
        ]

        checkgesprek: AppointmentTypeName = "Checkgesprek"
        toekomstgesprek: AppointmentTypeName = "Toekomstgesprek"
        if self.appointment_type.name == checkgesprek:
            content.append(
                "Deze afspraak zal telefonisch plaatsvinden. U wordt gebeld door de adviseur van Ondernemer Centraal."
            )
        elif self.appointment_type.name == toekomstgesprek:
            partner_org = self.partner_organization.name if self.partner_organization else None
            assert partner_org
            content.append(
                f"Deze afspraak zal telefonisch plaatsvinden. U wordt gebeld door een adviseur van onze partner {partner_org}"  # noqa: E501
            )

        return content

    @property
    def required_forms(self):
        allowed_form_name_mapping: dict[AppointmentTypeName, list[FormNames]] = {
            "Checkgesprek": ["Checkgesprek"],
            "Toekomstgesprek": ["Toekomstgesprek"],
            "SHVO intake": [],
        }
        assert self.appointment_type.name in allowed_form_name_mapping, (
            f"Appointment type {self.appointment_type.name} does not have required forms defined."
        )
        return [RequiredFormTemplate(name=f) for f in allowed_form_name_mapping[self.appointment_type.name]]

    @property
    def case_number(self):
        return self.case.case_number

    @property
    def client_initials(self):
        return self.case.client_initials

    @property
    def client_last_name(self):
        return self.case.client_last_name

    @property
    def client_residence_location(self):
        return self.case.client.residence_location

    @property
    def client_phone_number(self):
        return self.case.client.phone_number

    @property
    def client_email(self):
        return self.case.client.email
