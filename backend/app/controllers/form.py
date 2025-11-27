import datetime
import json
from dataclasses import dataclass
from typing import Literal

from fastapi import HTTPException, status
from jsonschema import Draft202012Validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import form_schemas
from app.config.permission_types import Permissions
from app.core.models import Appointment, Case, FormData, FormTemplate, Request, Track, User
from app.core.types import FormNames, FormStatus
from app.middleware.email_notification import EmailNotifier
from app.schemas.form_data import FormDataUpsert
from app.util.logger import logger


def get_schema(form_name: FormNames):
    with open(form_schemas[form_name], "r") as f:
        schema = json.load(f)
    return schema


def validate_payload(form_name: FormNames, payload: dict):
    schema = get_schema(form_name)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))

    if len(errors) > 0:
        for e in errors:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Het formulier is niet correct ingevuld."
            )
    return


MediaTypes = Literal["text/csv", "application/pdf"]
Extensions = Literal[".csv", ".pdf"]


@dataclass
class FormController:
    user: User
    session: AsyncSession | None = None
    track: Track | None = None
    appointment: Appointment | None = None
    request: Request | None = None

    @property
    def __base_query(self):
        """
        Returns a query that selects files from only the provided case or track.
        """
        if not self.user.has_permission("form:read-all"):
            assert self.track is not None or self.appointment is not None or self.request is not None, (
                "Either track, request or appointment must be provided"
            )

        query = select(FormData).options(
            joinedload(FormData.appointment).joinedload(Appointment.case).joinedload(Case.client),
            joinedload(FormData.track).joinedload(Track.case).joinedload(Case.client),
            joinedload(FormData.request).joinedload(Request.case).joinedload(Case.client),
        )
        if self.track:
            assert self.track.id is not None, "Track ID must be set"
            query = query.where(FormData.track_id == self.track.id)
        elif self.appointment:
            assert self.appointment.id is not None, "Appointment ID must be set"
            query = query.where(FormData.appointment_id == self.appointment.id)
        elif self.request:
            assert self.request.id is not None, "Request ID must be set"
            query = query.where(FormData.request_id == self.request.id)
        return query

    @property
    def _session(self):
        assert self.session
        return self.session

    def __validate_form_authorization(self, form_data: FormData):
        """
        Raise an HTTP error when the form does not belong to the specified track or appointment
        """
        if self.track and form_data.track_id != self.track.id:
            logger.error(
                f"Form {form_data.id} does not belong to track {self.track.id}, but to {form_data.track_id}"  # noqa: E501
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Form does not belong to specified track"
            )
        elif self.appointment and form_data.appointment_id != self.appointment.id:
            logger.error(
                f"Form {form_data.id} does not belong to appointment {self.appointment.id}, but to do {form_data.appointment_id}"  # noqa: E501
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Form does not belong to specified appointment"
            )

    def __validate_user_permission_and_raise_http_error(self, required_permission: Permissions):
        if not self.user.has_permission(required_permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    def __validate_user_permissions(self, form_template: FormTemplate):
        required_permission = form_template.required_permission
        self.__validate_user_permission_and_raise_http_error(required_permission)

    async def get_forms(self):
        forms = list((await self._session.scalars(self.__base_query)).unique())
        return [f for f in forms if self.user.has_permission(f.form_template.required_permission)]

    @property
    def __allowed_form_names(self):
        if self.track is not None:
            return self.track.required_forms
        elif self.appointment is not None:
            return self.appointment.required_forms
        elif self.request is not None:
            return self.request.required_forms

    async def get_form_data(self, form_template: FormTemplate, user: User):
        form_data_list = await self.get_forms()
        form_data_list_for_template_name = [f for f in form_data_list if f.form_template.name == form_template.name]

        n_forms = len(form_data_list_for_template_name)
        assert n_forms <= 1, f"There should be at most one form data for the given form template, found: {n_forms}."
        form_data = form_data_list_for_template_name[0] if n_forms > 0 else None

        # check if user has access to the track
        if (
            user.has_role("partner")
            and form_data is not None
            and form_data.track
            and form_data.track.partner_organization != user.partner_organization
        ):
            logger.error(f"User {user.name} does not have access to form from track {form_data.track.id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return form_data

    async def create_form_data(
        self,
        form_template: FormTemplate,
    ):
        self.__validate_user_permissions(form_template)

        assert self.__allowed_form_names is not None, (
            "Allowed form names should be defined for the current track or appointment."
        )
        if form_template.name not in [f.name for f in self.__allowed_form_names]:
            logger.error(f"Form {form_template.name} is not allowed for the current track or appointment.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Het formulier {form_template.name} is niet toegestaan.",  # noqa: E501
            )

        related_objects = [self.track, self.appointment, self.request]
        assert any([o is not None for o in related_objects]), (
            "At least one of track, appointment or request must be provided"
        )

        form_data = FormData(
            form_template=form_template, track=self.track, appointment=self.appointment, request=self.request
        )
        self._session.add(form_data)
        await self._session.flush()
        await self._session.refresh(form_data)
        return form_data

    async def upsert_form_data(
        self,
        form_data_upsert: FormDataUpsert,
        form_data: FormData,
        user: User,
    ):
        payload_has_changed = form_data.payload is not None and form_data.payload != form_data_upsert.payload

        if (form_data.approved or form_data.submitted) and payload_has_changed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Het formulier {form_data.form_template.name} is al ingediend of goedgekeurd en kan niet meer worden aangepast.",  # noqa: E501
            )

        payload_validation = (
            form_data.get_payload_validation(form_data_upsert.payload) if form_data_upsert.payload else None
        )
        payload_is_valid = payload_validation.is_valid if payload_validation else False

        if form_data_upsert.payload is not None and payload_is_valid:
            form_data.payload = form_data_upsert.payload
            form_data.payload_unvalidated = None
        elif form_data_upsert.payload is not None:
            form_data.payload_unvalidated = form_data_upsert.payload
            form_data.payload = None

        form_data.last_updated_by_user = user
        await self._session.flush()
        # Refresh to get 'updated_at' value
        await self._session.refresh(form_data)
        self.__validate_form_authorization(form_data)

        return form_data


async def update_form_status(form_data: FormData, user: User, target_status: FormStatus, email_notifier: EmailNotifier):
    form_data.last_updated_by_user = user

    current_status = form_data.status
    approval_permission_required = current_status == FormStatus.APPROVED or target_status == FormStatus.APPROVED
    if approval_permission_required and not user.has_permission("form:approve"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

    if target_status == FormStatus.APPROVED:
        form_data.approved = True
        form_data.approved_at = timestamp
        handle_approval_notification(form_data, approved=True, email_notifier=email_notifier)
    elif target_status == FormStatus.SUBMITTED or (target_status == FormStatus.APPROVED and not form_data.submitted):
        form_data.submitted = True
        form_data.submitted_at = timestamp
    else:
        form_data.approved = False
        form_data.approved_at = None
        form_data.submitted = False
        form_data.submitted_at = None


def handle_approval_notification(form_data: FormData, approved: bool, email_notifier: EmailNotifier):
    if form_data.track:
        partner_organization = form_data.track.partner_organization
    elif form_data.appointment:
        partner_organization = form_data.appointment.partner_organization
    else:
        partner_organization = None

    if approved and partner_organization is not None:
        email_notifier.notify_partner_organization(
            partner_organization=partner_organization,
            content=[f"Het formulier '{form_data.form_template_name}' is goedgekeurd."],
            subject="Formulier goedgekeurd",
        )
