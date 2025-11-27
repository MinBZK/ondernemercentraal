from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.client as schemas
from app.controllers import client as client_controller
from app.core.exceptions import InvalidInput
from app.core.models import Client, Role, User
from app.core.services import keycloak_service
from app.core.types import RoleNames
from app.middleware.dependencies import get_client, get_db_session, get_email_notifier
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker
from app.schemas.user import UserCreated

router = APIRouter(prefix="/client", tags=["client"])


@router.get("/{client_id}", response_model=schemas.Client, dependencies=[Depends(PermissionChecker("client:read"))])
async def fetch_client(
    client: Client = Depends(get_client),
):
    return client


@router.post(
    "/{client_id}/user", dependencies=[Depends(PermissionChecker("client:create-user"))], response_model=UserCreated
)
async def create_user(
    email_notifier: EmailNotifier = Depends(get_email_notifier),
    client: Client = Depends(get_client),
    session: AsyncSession = Depends(get_db_session),
):
    if client.active_case is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client does not have an active case. Cannot create user.",
        )
    if not client.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Het e-mailadres van de ondernemer is nog niet bevestigd. Een account kan daarom niet worden aangemaakt.",  # noqa: E501
        )
    required_role_name: RoleNames = "ondernemer"
    role = await session.scalar(select(Role).where(Role.name == required_role_name))
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role {required_role_name} does not exist")
    username = client.email

    user = await session.scalar(select(User).where(User.name == username))
    if not user:
        user = User(name=username, role=role, client=client, active=True)
        session.add(user)
    else:
        user.client = client

    try:
        credentials = keycloak_service.upsert_user(username)
        assert user.client, "User is not associated with a client"
        active_case = user.client.active_case
        assert active_case, "User is not associated with an active case"
        email_notifier.notify_user(
            user=user,
            subject="Er is een gebruikersaccount voor u aangemaakt",
            content=[
                "Ondernemer Centraal heeft voor u een account aangemaakt, zodat u uw eigen dossier kunt inzien.",
                "Er is een tijdelijk wachtwoord voor u ingesteld.",
                "Het tijdelijke wachtwoord is: " + credentials.password,
                "Klik op onderstaande link om uw dossier in te zien. U wordt eerst gevraagd om uw account in te stellen.",  # noqa: E501
            ],
            case=active_case,
            case_link_label="Bekijk uw dossier.",
        )
        return UserCreated(name=username, password=credentials.password, has_email=user.email is not None)
    except InvalidInput as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{client_id}", dependencies=[Depends(PermissionChecker("client:update"))])
async def update_client(
    client_update: schemas.ClientUpdate,
    client: Client = Depends(get_client),
    email_notifier: EmailNotifier = Depends(get_email_notifier),
) -> schemas.ClientUpdateResponse:
    if client.email != client_update.details.email:
        message = "Het e-mail van de ondernemer is gewijzigd. Er is een e-mail verstuurd naar de ondernemer met het verzoek om het nieuwe e-mailadres te bevestigen."  # noqa: E501
    else:
        message = None
    client_controller.update_client(client, client_update, email_notifier=email_notifier)
    return schemas.ClientUpdateResponse(message=message)
