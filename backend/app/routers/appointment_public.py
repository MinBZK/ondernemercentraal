import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.appointment import AppointmentController
from app.core.models import Appointment, Client
from app.core.types import AppointmentTypeName
from app.middleware.dependencies import get_appointment_type, get_client_from_token, get_db_session, get_email_notifier
from app.middleware.email_notification import EmailNotifier
from app.schemas.appointment import AppointmentNew

router = APIRouter(prefix="/appointment-public", tags=["appointment"])


def send_appointment_confirmation_mail(appointment: Appointment, email_notifier: EmailNotifier):
    content = appointment.get_confirmation_mail_content()

    assert appointment.case
    email_notifier.notify_client(client=appointment.case.client, subject="Afspraakbevestiging", content=content)


@router.post("/")
async def create_initial_appointment(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    client: Client = Depends(get_client_from_token),
    email_notifier: EmailNotifier = Depends(get_email_notifier),
    session: AsyncSession = Depends(get_db_session),
):
    if client.active_case and client.active_case.initial_appointment is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Het is niet mogelijk om u aan te melden omdat er al een lopende aanmelding bestaat.",
        )

    assert client.active_case, "Client must have an active case to create an appointment"
    client.email_confirmed = True
    appointment_type_name: AppointmentTypeName = "Checkgesprek"
    appointment_type = await get_appointment_type(appointment_type_name, session)
    await AppointmentController(session).create_appointment(
        appointment_type=appointment_type,
        email_notifier=email_notifier,
        case=client.active_case,
        appointment_new=AppointmentNew(
            start_time=start_time,
            end_time=end_time,
            appointment_type_name=appointment_type_name,
            partner_organization_name=None,
            status="Open",
        ),
    )

    return
