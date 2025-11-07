from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.controllers.client as client_controller
import app.schemas.client as schemas
from app.controllers import Client as ClientController
from app.core.models import Client
from app.core.services import keycloak_service
from app.core.settings import settings
from app.middleware.dependencies import get_client_from_token, get_db_session, get_email_notifier
from app.middleware.email_notification import EmailNotifier
from app.util.logger import logger

router = APIRouter(prefix="/client", tags=["client"])

FormTypes = Literal["Location", "Details"]


@router.get("/client-from-token", response_model=schemas.ClientWithCasePublic)
async def validate_token(client: Client = Depends(get_client_from_token)):
    return client


@router.post("/validation")
async def create_validation(
    client_location: schemas.ClientLocation,
) -> client_controller.ValidationResult:
    return client_controller.validate_location(client_location)


@router.post("/", response_model=schemas.Client)
async def create_client(
    client_new: schemas.ClientNew,
    email_notifier: EmailNotifier = Depends(get_email_notifier),
    session: AsyncSession = Depends(get_db_session),
):
    # Check if client already exists
    query = ClientController.base_query().where(Client.email == client_new.details.email)
    client = await session.scalar(query)

    if client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client already exists")

    client = client_controller.create_client(client_new, session)

    await session.flush()
    client_controller.send_appointment_pick_confirmation_email(client, email_notifier=email_notifier)
    return client


@router.post("/resend-confirmation-request")
async def send_confirmation(
    client_id: UUID | None = None,
    email: str | None = None,
    email_notifier: EmailNotifier = Depends(get_email_notifier),
    session: AsyncSession = Depends(get_db_session),
):
    query = ClientController.base_query()
    if client_id is None and email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either client id or email required")
    if client_id:
        query = query.where(Client.id == client_id)
    elif email:
        query = query.where(Client.email == email)
    else:
        raise NotImplementedError()
    client = await session.scalar(query)
    if client:
        client_controller.send_appointment_pick_confirmation_email(client, email_notifier)
    else:
        logger.warning(f"Client not found for id={client_id} or email={email}")


@router.post("/{client_id}/confirm-email")
async def confirm_email(
    client: Client = Depends(get_client_from_token),
    email_notifier: EmailNotifier = Depends(get_email_notifier),
):
    if client.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already confirmed.",
        )

    client.email_confirmed = True
    if client.user:
        credentials = keycloak_service.update_username(client.user.name, target_username=client.email)
        client.user.name = client.email
        email_notifier.notify_user(
            user=client.user,
            subject="Er is een gebruikersaccount voor u aangemaakt",
            content=[
                "Ondernemer Centraal heeft een nieuw account voor u aangemaakt. "
                "Er is een tijdelijk wachtwoord voor u ingesteld.",
                f"Uw gebruikersnaam is: <strong>{client.user.name}</strong>. "
                "Het tijdelijke wachtwoord is: " + credentials.password,
                "Klik op onderstaande link om in te loggen en uw account opnieuw in te stellen",  # noqa: E501
                f"<a href='{settings.CLIENT_BASE_URL}/beheer/'>Portaal bekijken</a>",
            ],
        )

    pass
