import datetime
from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload

import app.core.models as models
from app.config.permissions import Permissions
from app.core.types import AppointmentTypeName
from app.middleware.email_notification import EmailNotifier
from app.middleware.exceptions import NoPermission
from app.schemas.appointment import AppointmentNew, AppointmentUpdate
from app.util.logger import logger

from .availability import AppointmentSlotWithCapacityAndUtilization, get_availability_data


def notify_partner_org(appointment: models.Appointment, email_notifier: EmailNotifier):
    content = [
        f"Ondernemer Centraal heeft uw organisatie toegewezen aan een gesprek met type '{appointment.appointment_type.name}'."  # noqa
    ]

    partner_organization = appointment.partner_organization
    assert partner_organization

    email_notifier.notify_partner_organization(
        partner_organization=partner_organization,
        content=content,
        subject=f"Gesprek met type '{appointment.appointment_type.name}' aangemaakt",
    )


async def validate_appointment_slot(session: AsyncSession, start_time: datetime.datetime, end_time: datetime.datetime):
    availability_data = await get_availability_data(session, start_time.date(), end_time.date())

    appointment_slot = AppointmentSlotWithCapacityAndUtilization(
        start_time=start_time,
        end_time=end_time,
        appointments=availability_data.appointments,
        availability_slots_defined_dated=availability_data.availability_slots_defined_dated,
        availability_slots_defined_default=availability_data.availability_slots_defined_default,
    )

    if not appointment_slot.has_advisor_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The chosen appointment slot has no available advisor",
        )


def get_required_product_name(appointment_type_name: AppointmentTypeName):
    if appointment_type_name == "Toekomstgesprek":
        return "Toekomstgesprek"
    elif appointment_type_name == "SHVO intake":
        return "SHVO intake"
    else:
        return None


@dataclass
class AppointmentController:
    session: AsyncSession

    def __check_permission(self, user: models.User, required_permission: Permissions):
        if not user.has_permission(required_permission):
            raise NoPermission(username=user.name, required_permission=required_permission)

    @property
    def __base_query(self):
        PartnerOrganizationAlias = aliased(models.PartnerOrganization)
        query = (
            select(models.Appointment)  # Select the Appointment object
            .join(models.Track, models.Appointment.track_id == models.Track.id, isouter=True)  # LEFT JOIN Track
            # LEFT JOIN PartnerOrganization for the direct link from Appointment
            .join(
                models.PartnerOrganization,
                models.Appointment.partner_organization_id == models.PartnerOrganization.id,
                isouter=True,
            )
            # LEFT JOIN PartnerOrganization for the Track's partner using the alias
            .join(
                PartnerOrganizationAlias,
                models.Track.partner_organization_id == PartnerOrganizationAlias.id,
                isouter=True,
            )
            # Join to User via the PartnerOrganization that is being filtered
            # We need to join to the original PartnerOrganization and the aliased one
            .join(
                models.User,
                or_(
                    models.User.partner_organization_id == models.PartnerOrganization.id,  # Direct link
                    models.User.partner_organization_id == PartnerOrganizationAlias.id,  # Link through Track
                ),
                isouter=True,
            )
            .options(
                joinedload(models.Appointment.track).joinedload(models.Track.forms),
                joinedload(models.Appointment.forms).joinedload(models.FormData.form_template),
                joinedload(models.Appointment.appointment_type),
                selectinload(models.Appointment.case).joinedload(models.Case.client),
                selectinload(models.Appointment.case).joinedload(models.Case.advisor),
            )
        )
        return query

    async def get_many(self, user: models.User, case: models.Case | None):
        """
        Returns appointments that are linked to the user either directly or through a track's partner organization.
        """

        query = self.__base_query

        if user.has_role("partner"):
            query = query.where(models.User.id == user.id)

        if case:
            query = query.where(models.Appointment.case_id == case.id)

        return list((await self.session.scalars(query)).unique().all())

    async def get_one(self, appointment_id: UUID):
        return await self.session.scalar(self.__base_query.where(models.Appointment.id == appointment_id))

    async def __get_partner_organization(self, partner_organization_name: str):
        return await self.session.scalar(
            select(models.PartnerOrganization).where(models.PartnerOrganization.name == partner_organization_name),
        )

    async def update_appointment(
        self,
        user: models.User,
        email_notifier: EmailNotifier,
        appointment_update: AppointmentUpdate,
        appointment: models.Appointment,
        appointment_type_update: models.AppointmentType,
    ):
        target_type_name: AppointmentTypeName = "SHVO intake"
        if (
            appointment.appointment_type.name == target_type_name
            and appointment_update.appointment_type_name != target_type_name
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Een gesprek met type '{target_type_name} mag niet van type geworden gewijzigd.",
            )

        if (
            appointment_update.start_time
            and appointment_update.end_time
            and appointment.appointment_type.name == "Checkgesprek"
            and appointment.start_time != appointment_update.start_time
            and appointment.end_time != appointment_update.end_time
        ):
            await validate_appointment_slot(self.session, appointment_update.start_time, appointment_update.end_time)

        if appointment.start_time != appointment_update.start_time:
            target_appointment_type_names: list[AppointmentTypeName] = ["SHVO intake", "Toekomstgesprek"]
            if appointment.appointment_type.name in target_appointment_type_names:
                self.__check_permission(user, "appointment:update:date")
            else:
                self.__check_permission(user, "appointment:update")

            appointment.start_time = appointment_update.start_time
            appointment.end_time = appointment_update.end_time

        appointment.appointment_type = appointment_type_update
        if appointment.status != appointment_update.status:
            target_appointment_type_names: list[AppointmentTypeName] = ["SHVO intake", "Toekomstgesprek"]
            if appointment.appointment_type.name in target_appointment_type_names:
                self.__check_permission(user, "appointment:update:status")
            else:
                self.__check_permission(user, "appointment:update")
            appointment.status = appointment_update.status
            content = [
                f"De status van uw gesprek '{appointment_update.appointment_type_name}' is gewijzigd naar '{appointment_update.status}'"  # noqa: E501
            ]
            email_notifier.notify_client(
                client=appointment.case.client,
                subject="Gesprekstatus gewijzigd",
                content=content,
            )
            if not appointment.case.advisor:
                logger.warning(f"Appointment {appointment.id} has no advisor, cannot notify user for status change.")
                return
            email_notifier.notify_user(
                subject="Gesprekstatus gewijzigd",
                content=[
                    f"De status van het gesprek '{appointment_update.appointment_type_name}' is gewijzigd naar '{appointment_update.status}'"  # noqa: E501
                ],
                user=appointment.case.advisor,
            )

        new_partner_organization_name = appointment_update.partner_organization_name
        existing_partner_organization_name = (
            appointment._partner_organization.name if appointment._partner_organization else None
        )
        if new_partner_organization_name != existing_partner_organization_name:
            self.__check_permission(user, "appointment:update")
            new_partner_organization = (
                await self.__get_partner_organization(appointment_update.partner_organization_name)
                if appointment_update.partner_organization_name
                else None
            )
            appointment.partner_organization = new_partner_organization

        if appointment_update.partner_organization_name is not None:
            notify_partner_org(appointment, email_notifier)

        if appointment_update.start_time != appointment.start_time:
            content = appointment.get_confirmation_mail_content()
            email_notifier.notify_client(
                client=appointment.case.client,
                subject=f"Gesprek ingepland ({appointment.appointment_type.name})",
                content=content,
            )

    async def create_appointment(
        self,
        email_notifier: EmailNotifier,
        case: models.Case,
        appointment_new: AppointmentNew,
        appointment_type: models.AppointmentType,
    ):
        # A checkgesprek is done by the advisor.
        # Check the availability of the advisor for the requested appointment slot
        if (
            appointment_new.start_time
            and appointment_new.end_time
            and appointment_new.appointment_type_name == "Checkgesprek"
        ):
            await validate_appointment_slot(self.session, appointment_new.start_time, appointment_new.end_time)

        if appointment_new.partner_organization_name:
            partner_org = await self.__get_partner_organization(appointment_new.partner_organization_name)
        else:
            partner_org = None

        if partner_org is not None:
            available_product_names = partner_org.product_names
            required_product_name = get_required_product_name(appointment_type.name)
            assert required_product_name in available_product_names, (
                f"Partner organization {partner_org.name} does not support the required product "
                f"{required_product_name} for appointment type {appointment_type.name}."
                f"The available products are: {available_product_names}."
            )

        new_appointment = models.Appointment(
            start_time=appointment_new.start_time,
            end_time=appointment_new.end_time,
            case=case,
            appointment_type=appointment_type,
            status=appointment_new.status,
            partner_organization=partner_org,
        )
        self.session.add(new_appointment)

        if new_appointment.partner_organization_name is not None and new_appointment.start_time is not None:
            notify_partner_org(new_appointment, email_notifier)

        if new_appointment.start_time is not None and new_appointment.appointment_type.name != "Checkgesprek":
            notification_content = new_appointment.get_confirmation_mail_content()
            email_notifier.notify_client(
                client=new_appointment.case.client,
                subject=f"Gesprek ingepland ({new_appointment.appointment_type.name})",
                content=notification_content,
            )

        return new_appointment
