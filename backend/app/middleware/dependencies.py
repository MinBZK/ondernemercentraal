from uuid import UUID

from fastapi import BackgroundTasks, Depends, HTTPException, status
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.core.models as models
from app.controllers.appointment import AppointmentController
from app.controllers.comment import CommentController
from app.controllers.file import FileController
from app.controllers.form import FormController
from app.controllers.misc import Case as CaseController
from app.controllers.misc import Client as ClientController
from app.core import settings
from app.core.access_control import keycloak_auth
from app.core.database import async_session
from app.core.types import AppointmentTypeName, FormNames
from app.middleware.confirmation_token import TokenValidationResponse
from app.middleware.email_notification import EmailNotifier
from app.util.logger import logger


async def get_db_session():
    # https://docs.sqlalchemy.org/en/20/core/connections.html#begin-once
    # context-manager automatically commits() the session after yield.  Only flushing necessary
    async with async_session.begin() as session:
        yield session


async def get_username_from_token(
    token: str = Depends(keycloak_auth.oauth2_scheme),
) -> str:
    if settings.DISABLE_AUTH == "0":
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        decoded_token = keycloak_auth.decode_token(token)
        return decoded_token["preferred_username"]
    else:
        return settings.DEFAULT_ADMIN_USERNAME


async def get_logged_in_user(
    session: AsyncSession = Depends(get_db_session), username: str = Depends(get_username_from_token)
):
    user = await session.scalar(
        select(models.User)
        .where(models.User.name == username)
        .options(
            joinedload(models.User.role),
            joinedload(models.User.partner_organization),
            joinedload(models.User.client).joinedload(models.Client.cases),
        )
    )

    if not user:
        logger.warning(f"User {username} not found in database")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not user.active:
        logger.warning(f"User {username} is not active")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user


async def get_client(
    client_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    user: models.User = Depends(get_logged_in_user),
):
    query = ClientController.base_query().where(models.Client.id == client_id)
    client = await session.scalar(query)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if user.has_role("ondernemer"):
        assert user.client
        if user.client.id != client.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    elif user.has_role("partner"):
        if not user.partner_organization or client.active_case is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        if not client.active_case.has_link_to_partner_organization(user.partner_organization):
            logger.error(
                f"User {user.name} with role {user.role_name} does not have access to client {client.id}, because there is no link through the partner organization {user.partner_organization.id}"  # noqa: E501
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return client


async def get_appointment_type(
    appointment_type_name: AppointmentTypeName,
    session: AsyncSession,
):
    appointment_type = await session.scalar(
        select(models.AppointmentType).where(models.AppointmentType.name == appointment_type_name),
    )
    assert appointment_type
    return appointment_type


async def get_case(
    case_id: UUID,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    query = CaseController.base_query().where(models.Case.id == case_id)
    case = await session.scalar(query)

    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    if not case.is_linked_to_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return case


async def get_file(
    file_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    base_query = select(models.File)
    file = await session.scalar(base_query.where(models.File.id == file_id))
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file


async def get_track_type(
    track_type_name: str,
    session: AsyncSession = Depends(get_db_session),
):
    track_type = await session.scalar(
        select(models.TrackType).where(models.TrackType.name == track_type_name),
    )
    assert track_type
    return track_type


async def get_partner_organization(
    partner_organization_name: str,
    session: AsyncSession = Depends(get_db_session),
):
    partner_organization = await session.scalar(
        select(models.PartnerOrganization).where(models.PartnerOrganization.name == partner_organization_name),
    )
    assert partner_organization
    return partner_organization


async def get_partner_organization_by_id(
    partner_organization_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    partner_organization = await session.scalar(
        select(models.PartnerOrganization)
        .where(models.PartnerOrganization.id == partner_organization_id)
        .options(joinedload(models.PartnerOrganization.products)),
    )
    if partner_organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner organization not found")
    return partner_organization


async def get_track(
    track_id: UUID,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    base_query = select(models.Track).options(
        joinedload(models.Track.forms).joinedload(models.FormData.form_template),
        joinedload(models.Track.track_type),
        joinedload(models.Track.case).joinedload(models.Case.tasks),
        joinedload(models.Track.partner_organization),
        joinedload(models.Track.case).joinedload(models.Case.client),
        joinedload(models.Track.appointments).joinedload(models.Appointment.forms),
        joinedload(models.Track.appointments).joinedload(models.Appointment.case).joinedload(models.Case.client),
    )
    track = await session.scalar(base_query.where(models.Track.id == track_id))
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")

    # check if user has access to the track
    if user.has_role("partner") and track.partner_organization != user.partner_organization:
        logger.error(f"User {user.name} does not have access to track {track.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return track


async def get_appointment(
    appointment_id: UUID,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    appointment = await AppointmentController(session).get_one(appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    # check if user has access to the track
    if user.has_role("partner") and appointment.partner_organization != user.partner_organization:
        logger.error(f"User {user.name} does not have access to appointment {appointment.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return appointment


async def get_form_template(
    form_name: FormNames,
    session: AsyncSession = Depends(get_db_session),
):
    form_template = await session.scalar(select(models.FormTemplate).where(models.FormTemplate.name == form_name))
    assert form_template, f"Form template {form_name} not found"
    return form_template


async def get_optional_case(
    case_id: UUID | None = None,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    if case_id:
        return await get_case(case_id, user, session)


async def get_optional_track(
    track_id: UUID | None = None,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    if track_id:
        return await get_track(track_id, user, session)


async def get_optional_appointment(
    appointment_id: UUID | None = None,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    if appointment_id:
        return await get_appointment(appointment_id, user, session)


async def get_optional_request(
    request_id: UUID | None = None,
    user: models.User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    if request_id:
        return await get_request(request_id=request_id, session=session, user=user)


async def get_file_controller(
    session: AsyncSession = Depends(get_db_session),
    case: models.Case | None = Depends(get_optional_case),
    track: models.Track | None = Depends(get_optional_track),
    appointment: models.Appointment | None = Depends(get_optional_appointment),
    user: models.User = Depends(get_logged_in_user),
):
    return FileController(session=session, case=case, track=track, appointment=appointment, user=user)


async def get_comment_controller(
    session: AsyncSession = Depends(get_db_session),
    case: models.Case | None = Depends(get_optional_case),
    track: models.Track | None = Depends(get_optional_track),
    appointment: models.Appointment | None = Depends(get_optional_appointment),
    user: models.User = Depends(get_logged_in_user),
):
    return CommentController(session=session, case=case, track=track, appointment=appointment, user=user)


async def get_request(
    request_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    user: models.User = Depends(get_logged_in_user),
):
    request = await session.scalar(
        select(models.Request).where(models.Request.id == request_id).options(joinedload(models.Request.case))
    )
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if not request.case.is_linked_to_user(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this request")

    return request


async def get_form_controller(
    session: AsyncSession = Depends(get_db_session),
    track: models.Track | None = Depends(get_optional_track),
    appointment: models.Appointment | None = Depends(get_optional_appointment),
    request: models.Request | None = Depends(get_optional_request),
    user: models.User = Depends(get_logged_in_user),
):
    return FormController(session=session, track=track, appointment=appointment, user=user, request=request)


async def get_form_data_by_id(
    form_data_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    base_query = select(models.FormData)
    form_data = await session.scalar(base_query.where(models.FormData.id == form_data_id))
    if not form_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form data not found")

    return form_data


async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    user = await session.scalar(select(models.User).where(models.User.id == user_id))
    return user


def get_email_notifier(
    background_task: BackgroundTasks,
):
    return EmailNotifier(background_task)


async def get_client_from_token(
    token: str,
    session: AsyncSession = Depends(get_db_session),
):
    try:
        client_id = UUID(TokenValidationResponse(token=token).decoded_token.client_id)
        client = await session.scalar(ClientController.base_query().where(models.Client.id == client_id))
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return client
    except InvalidTokenError as e:
        logger.warning(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")


async def get_product_category(
    product_category_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    product_category = await session.scalar(
        select(models.ProductCategory)
        .where(models.ProductCategory.id == product_category_id)
        .options(joinedload(models.ProductCategory.products))
    )
    if not product_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product category not found")
    return product_category


async def get_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    product = await session.scalar(select(models.Product).where(models.Product.id == product_id))
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    task = await session.scalar(select(models.Task).where(models.Task.id == task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


async def get_form_data(
    form_data_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    user: models.User = Depends(get_logged_in_user),
):
    form_data = await session.scalar(
        select(models.FormData)
        .where(models.FormData.id == form_data_id)
        .options(
            joinedload(models.FormData.appointment)
            .joinedload(models.Appointment.case)
            .joinedload(models.Case.appointments),
            joinedload(models.FormData.track).joinedload(models.Track.case).joinedload(models.Case.tracks),
            joinedload(models.FormData.request).joinedload(models.Request.case).joinedload(models.Case.requests),
        )
    )
    if not form_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form data not found")

    user_linked_to_request = form_data.request and form_data.request.case.is_linked_to_user(user)
    user_linked_to_appointment = form_data.appointment and form_data.appointment.case.is_linked_to_user(user)
    user_linked_to_track = form_data.track and form_data.track.case.is_linked_to_user(user)
    user_is_linked = any([user_linked_to_request, user_linked_to_appointment, user_linked_to_track])
    if not user_is_linked and not user.has_permission("form:read-all"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return form_data
