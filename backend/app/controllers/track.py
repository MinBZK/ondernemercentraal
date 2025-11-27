import datetime
from dataclasses import dataclass

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.middleware.dependencies as deps
from app.config import track_completion_causes
from app.config.permissions import Permissions
from app.core.models import (
    Appointment,
    Case,
    FormData,
    PartnerOrganization,
    Product,
    ProductCategory,
    Task,
    Track,
    User,
)
from app.core.models.task import TaskStatus
from app.core.types import AppointmentStatus, TrackStatus, TrackTypes
from app.middleware.exceptions import NoPermission
from app.schemas.track import TrackCreate, TrackUpdate


@dataclass
class TrackController:
    @classmethod
    def base_query(cls, user: User):
        query = (
            select(Track)
            .join(PartnerOrganization, isouter=True)
            .join(User, isouter=True)
            .options(
                joinedload(Track.track_type),
                joinedload(Track.partner_organization).joinedload(PartnerOrganization.products),
                joinedload(Track.appointments).joinedload(Appointment.forms),
                joinedload(Track.appointments).joinedload(Appointment.case).joinedload(Case.client),
                joinedload(Track.forms).joinedload(FormData.form_template),
                joinedload(Track.case).joinedload(Case.client),
                joinedload(Track.case).joinedload(Case.advisor).joinedload(User.role),
            )
        )
        if user and user.has_role("partner"):
            query = query.where(User.id == user.id)
        return query

    @classmethod
    async def get_many(cls, session: AsyncSession, user: User, case: Case | None):
        query = cls.base_query(user)
        if case:
            query = query.where(Track.case_id == case.id)
        return list((await session.scalars(query)).unique().all())

    def update_track_status(self, track: Track, target_track_status: TrackStatus, completion_cause: str | None):
        required_track_status: TrackStatus = "Beëindigd"
        if completion_cause is not None and target_track_status != required_track_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Beëindigsreden mag alleen worden ingevuld wanneer de status gelijk is aan {required_track_status}.",  # noqa
            )

        current_status = track.status

        status_sequence: list[TrackStatus] = ["Nog niet gestart", "Gestart", "Beëindigd"]

        next_index = status_sequence.index(current_status) + 1

        allowed_target_status = status_sequence[next_index] if next_index < len(status_sequence) else None
        if allowed_target_status != target_track_status and target_track_status != current_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status kan niet worden gewijzigd van '{current_status}' naar '{target_track_status}'.",
            )

        if target_track_status == "Gestart":
            track.start_dt = datetime.datetime.now(tz=datetime.timezone.utc)

        if target_track_status == "Beëindigd":
            track.end_dt = datetime.datetime.now(tz=datetime.timezone.utc)
            if completion_cause is None or completion_cause not in track_completion_causes:
                detail = (
                    f"Beëindigsreden '{completion_cause}' is ongeldig."
                    if completion_cause
                    else "Beëindigsreden is verplicht."
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail,
                )
            track.completion_cause = completion_cause

    @staticmethod
    def __validate_user_permission(user: User, required_permission: Permissions):
        if not user.has_permission(required_permission):
            raise NoPermission(username=user.name, required_permission=required_permission)

    async def __update_track_product(
        self,
        track: Track,
        new_product_name: str | None,
        session: AsyncSession,
        user: User,
        partner_organization: PartnerOrganization | None,
    ):
        product = await session.scalar(select(Product).where(Product.name == new_product_name))
        if new_product_name is not None and product is None:
            assert product, f"Product '{new_product_name}' not found."

        new_product_id = product.id if product else None
        if new_product_id != track.product_id:
            self.__validate_user_permission(user, "track:update:product")
            track.product = product

        if new_product_name is not None and track.track_type.name != "Ondernemersdienstverlening":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product mag alleen worden aangepast voor Ondernemersdienstverlening trajecten.",
            )

        if new_product_name is not None:
            assert product, f"Product '{new_product_name}' not found."

        if partner_organization and product:
            partner_org_has_product = product.name in [p for p in partner_organization.product_names]
            assert partner_org_has_product, (
                f"Partnerorganisatie '{partner_organization.name}' heeft geen toegang tot product '{product.name}'."
            )

    async def upsert_track(
        self,
        track: Track | None,
        track_update: TrackUpdate | TrackCreate,
        user: User,
        session: AsyncSession,
        case: Case | None = None,
    ):
        if track is None:
            assert case is not None, "Case must be provided when creating a new track."
            track = Track(completion_approved=False, case=case)
            session.add(track)

        track_type = await deps.get_track_type(track_update.track_type_name, session)
        partner_organization = (
            await deps.get_partner_organization(track_update.partner_organization_name, session)
            if track_update.partner_organization_name
            else None
        )

        if track_type.settings.partner_organization_required and not partner_organization:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Een partnerorganisatie is verplicht voor trajecttype '{track_type.name}'.",
            )

        if track_update.status and track_update.status != track.status:
            self.__validate_user_permission(user, "track:update:status")
            self.update_track_status(
                track=track,
                target_track_status=track_update.status,
                completion_cause=track_update.completion_cause,
            )

        if track_update.completion_approved != track.completion_approved:
            self.__validate_user_permission(user, "track:update:completion_approval")

            if not track_update.status == "Beëindigd":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Track status must be 'Beëindigd' to update completion approval.",
                )

            track.completion_approved = track_update.completion_approved

            if track_update.completion_approved:
                due_date = datetime.datetime.now(tz=datetime.timezone.utc) + relativedelta(months=6)
                track.case.tasks.append(
                    Task(
                        description="Traject beëindigd met goedkeuring door adviseur. Controleer of de ondernemer nog steeds tevreden is.",  # noqa: E501
                        due_date=due_date,
                        status=TaskStatus.TO_DO,
                    )
                )

        new_track_type_id = track_type.id if track_type else None
        new_partner_organization_id = partner_organization.id if partner_organization else None

        product_category = await session.scalar(
            select(ProductCategory).where(ProductCategory.name == track_update.product_category_name)
        )
        new_product_category_id = product_category.id if product_category else None
        if new_product_category_id != track.product_category_id:
            self.__validate_user_permission(user, "track:update:product-category")
            track.product_category = product_category

        if new_partner_organization_id != track.partner_organization_id:
            self.__validate_user_permission(user, "track:update:partner")
            track.partner_organization = partner_organization

        if new_track_type_id != track.track_type_id or new_partner_organization_id != track.partner_organization_id:
            self.__validate_user_permission(user, "track:update")
            track.track_type = track_type
            track.priority = track_update.priority

        await self.__update_track_product(
            track=track,
            new_product_name=track_update.product_name,
            session=session,
            user=user,
            partner_organization=partner_organization,
        )

        shvo_track_type: TrackTypes = "SHVO"
        if track_type.name == shvo_track_type:
            appointment_type = await deps.get_appointment_type("SHVO intake", session)
            initial_status: AppointmentStatus = "Open"
            assert track.case
            track.appointments.append(
                Appointment(appointment_type=appointment_type, case=track.case, status=initial_status)
            )

        return track
