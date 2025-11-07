from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.appointment import AppointmentController
from app.core.models import Appointment, Case, User
from app.middleware.dependencies import (
    get_appointment,
    get_appointment_type,
    get_case,
    get_db_session,
    get_logged_in_user,
    get_optional_case,
)
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker
from app.schemas.appointment import Appointment as AppointmentSchema
from app.schemas.appointment import AppointmentNew, AppointmentUpdate

router = APIRouter(prefix="/appointment", tags=["appointment"])


@router.post("/", dependencies=[Depends(PermissionChecker("appointment:create"))])
async def create_appointment(
    appointment_new: AppointmentNew,
    email_notifier: EmailNotifier = Depends(EmailNotifier),
    case: Case = Depends(get_case),
    session: AsyncSession = Depends(get_db_session),
):
    appointment_type = await get_appointment_type(appointment_new.appointment_type_name, session)
    await AppointmentController(session).create_appointment(
        appointment_type=appointment_type,
        email_notifier=email_notifier,
        case=case,
        appointment_new=appointment_new,
    )
    return


@router.delete("/{appointment_id}", dependencies=[Depends(PermissionChecker("appointment:delete"))])
async def delete_appointment(
    appointment: Appointment = Depends(get_appointment),
    session: AsyncSession = Depends(get_db_session),
):
    if appointment.track:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dit gesprek behoort toe aan een traject en kan niet worden verwijderd. Verwijder daarom eerst het traject.",  # noqa: E501
        )
    await session.delete(appointment)
    return


@router.put("/{appointment_id}")
async def update_appointment(
    appointment_update: AppointmentUpdate,
    email_notifier: EmailNotifier = Depends(EmailNotifier),
    appointment: Appointment = Depends(get_appointment),
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_logged_in_user),
):
    appointment_type = await get_appointment_type(appointment_update.appointment_type_name, session)
    await AppointmentController(session).update_appointment(
        user=user,
        email_notifier=email_notifier,
        appointment_update=appointment_update,
        appointment_type_update=appointment_type,
        appointment=appointment,
    )
    return


@router.get("/", response_model=list[AppointmentSchema], dependencies=[Depends(PermissionChecker("appointment:read"))])
async def get_appointments(
    case: Case = Depends(get_optional_case),
    user: User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await AppointmentController(session).get_many(user=user, case=case)


@router.get(
    "/{appointment_id}", response_model=AppointmentSchema, dependencies=[Depends(PermissionChecker("appointment:read"))]
)
async def fetch_appointment(appointment: Appointment = Depends(get_appointment)):
    return appointment
