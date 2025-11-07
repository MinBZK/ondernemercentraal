from fastapi import HTTPException, status
from pydantic import BaseModel, computed_field
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.client as schemas
from app.core.models import Case, Client
from app.core.settings import settings
from app.middleware.confirmation_token import ConfirmationTokenHandler
from app.middleware.email_notification import EmailNotifier
from app.util.logger import logger


def send_appointment_pick_confirmation_email(client: Client, email_notifier: EmailNotifier):
    token = ConfirmationTokenHandler().create_token(client.id)
    url = f"{settings.CLIENT_BASE_URL}/nl/appointment/pick?confirmation_token={token}"
    assert client.active_case
    content = [
        "Bedankt voor uw aanmelding bij Ondernemer Centraal.",
        "Om de aanmelding definitief te maken vragen wij u om een afspraak te maken.",
        f"<a href='{url}'>Klik hier om een afspraak te maken.</a>",
    ]

    email_notifier.notify_client(
        client=client,
        subject="Afspraak maken",
        content=content,
        email_must_be_confirmed=False,
    )
    logger.info(f"Confirmation url: {url}")
    return token


def send_email_confirmation_email(client: Client, email_notifier: EmailNotifier):
    token = ConfirmationTokenHandler().create_token(client.id)
    url = f"{settings.CLIENT_BASE_URL}/nl/client/confirm?confirmation_token={token}"
    assert client.active_case
    content = [
        "Uw e-mail adres bij Ondernemer Centraal is gewijzigd.",
        f"<a href='{url}'>Klik hier om uw e-mailadres te bevestigen.</a>",
    ]

    email_notifier.notify_client(
        client=client,
        subject="E-mailadres bevestigen",
        content=content,
        email_must_be_confirmed=False,
    )
    return token


class ValidationResult(BaseModel):
    errors: list[str]

    @computed_field
    @property
    def valid(self) -> bool:
        return len(self.errors) == 0


def validate_location(client: schemas.ClientLocation):
    allowed_gemeentes = settings.tenant_config["allowed_gemeentes"]
    appointment_allowed = client.residence_location in allowed_gemeentes or client.company_location in allowed_gemeentes
    errors: list[str] = []
    if not appointment_allowed:
        errors.append("Appointment not allowed")
    return ValidationResult(errors=errors)


def create_client(client_new: schemas.ClientNew, session: AsyncSession):
    appointment_location_validation = validate_location(client_new.location)
    if not appointment_location_validation.valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appointment invalid")
    client_payload = client_new.location.model_dump() | client_new.details.model_dump()
    client = Client(email_confirmed=False, **client_payload, cases=[Case()])
    session.add(client)
    return client


def update_client(client: Client, client_update: schemas.ClientUpdate, email_notifier: EmailNotifier):
    client_payload = client_update.location.model_dump() | client_update.details.model_dump()

    if client.agree_to_share_data != client_update.details.agree_to_share_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agree to share data update not allowed")

    for key, value in client_payload.items():
        if key != "email":
            setattr(client, key, value)

    if client.email != client_update.details.email:
        client.email = client_update.details.email
        client.email_confirmed = False
        send_email_confirmation_email(client=client, email_notifier=email_notifier)
