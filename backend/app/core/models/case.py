from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, ForeignKey, Identity, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.core.types import AppointmentTypeName

from .base_model import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment
    from .client import Client
    from .partner_organization import PartnerOrganization
    from .request import Request
    from .task import Task
    from .track import Track
    from .user import User


class Case(BaseModel):
    __tablename__ = "case"

    case_number: Mapped[int] = mapped_column(
        Integer, Identity(start=200, cycle=True), nullable=False, unique=True, primary_key=True
    )

    client_id: Mapped[UUID] = mapped_column(ForeignKey("client.id", ondelete="CASCADE"), nullable=False)

    client: Mapped[Client] = relationship("Client", back_populates="cases", lazy="joined")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment", back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )

    advisor_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=True)
    advisor: Mapped[User | None] = relationship("User", back_populates="cases", lazy="selectin")

    tracks: Mapped[list[Track]] = relationship(
        "Track",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tasks: Mapped[list[Task]] = relationship(
        "Task", back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    requests: Mapped[list[Request]] = relationship(
        "Request", back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def client_bsn(self):
        return self.client.bsn

    @property
    def client_last_name(self):
        return self.client.last_name

    @property
    def client_initials(self):
        return self.client.initials

    @property
    def initial_appointment(self):
        target_appointment_type: AppointmentTypeName = "Checkgesprek"
        return next(
            (
                appointment
                for appointment in self.appointments
                if appointment.appointment_type.name == target_appointment_type
            ),
            None,
        )

    @property
    def description(self):
        return f"Dossiernummer {str(self.case_number)} ({self.client.written_name})"

    @property
    def advisor_name(self):
        if self.advisor:
            return self.advisor.name

    @property
    def url(self):
        return f"{settings.CLIENT_BASE_URL}/beheer/case/{self.id}"

    def has_link_to_partner_organization(self, target_partner_organization: PartnerOrganization):
        case_has_track_linked_to_target_partner_org = any(
            t
            for t in self.tracks
            if t.partner_organization is not None and t.partner_organization.id == target_partner_organization.id
        )
        case_has_appointment_linked_to_target_partner_org = any(
            a
            for a in self.appointments
            if a.partner_organization is not None and a.partner_organization.id == target_partner_organization.id
        )
        return case_has_track_linked_to_target_partner_org or case_has_appointment_linked_to_target_partner_org

    def is_linked_to_user(self, user: User):
        """
        Return True if the user has access to this case, otherwise False.
        """

        if user.has_role("ondernemer") and user.client is not None:
            is_linked = user.client.active_case.id == self.id if user.client.active_case else False
            # if not is_linked:
            #     logger.debug(
            #         f"User {user.name} with role {user.role_name} does not have access to case {self.id}, because the user is not linked to the case through the client {user.client.id}"  # noqa: E501
            #     )
            return is_linked
        elif user.has_role("ondernemer"):
            # logger.debug(
            #     f"User {user.name} with role {user.role_name} does not have access to case {self.id}, because the user is not linked to a client"  # noqa: E501
            # )
            return False
        elif user.has_role("partner"):
            # target_partner_org_id = user.partner_organization.id if user.partner_organization else None
            partner_organization = user.partner_organization

            if not partner_organization:
                # logger.debug(
                #     f"User {user.name} with role {user.role_name} does not have access to case {self.id}, because the user is not linked to a partner organization"  # noqa: E501
                # )  # noqa: E501
                return False
            elif not self.has_link_to_partner_organization(partner_organization):
                # logger.debug(
                #     f"User {user.name} with role {user.role_name} does not have access to case {self.id}, because there is no link through the partner organization {target_partner_org_id}"  # noqa: E501
                # )
                return False
        return True
