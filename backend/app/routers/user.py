from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.controllers.user as user_controller
import app.middleware.dependencies as deps
import app.schemas.user as schemas
from app.core import settings
from app.core.models import Role, User
from app.core.services import keycloak_service
from app.core.types import RoleNames
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker
from app.util.logger import logger

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=list[schemas.User], dependencies=[Depends(PermissionChecker("user:read"))])
async def get_users(
    session: AsyncSession = Depends(deps.get_db_session),
):
    users = list(
        (
            await session.scalars(
                select(User).options(
                    joinedload(User.role), joinedload(User.partner_organization), joinedload(User.client)
                )
            )
        ).unique()
    )

    return users


@router.post("/", dependencies=[Depends(PermissionChecker("user:create"))], response_model=schemas.UserCreated)
async def create_user(
    user_new: schemas.UserCreate,
    email_notifier: EmailNotifier = Depends(deps.get_email_notifier),
    session: AsyncSession = Depends(deps.get_db_session),
):
    credentials, created_user = await user_controller.create_user(session=session, user_new=user_new)

    email_notifier.notify_user(
        user=created_user,
        subject="Er is een gebruikersaccount voor u aangemaakt",
        content=[
            "Ondernemer Centraal heeft voor u een account aangemaakt.",
            "Er is een tijdelijk wachtwoord voor u ingesteld.",
            "Het tijdelijke wachtwoord is: " + credentials.password,
            "Klik op onderstaande link om de portaal te bekijken:",  # noqa: E501
            f"<a href='{settings.CLIENT_BASE_URL}/beheer/'>Ondernemer Centraal</a>",
        ],
    )

    return schemas.UserCreated(
        name=user_new.name, password=credentials.password, has_email=created_user.email is not None
    )


@router.put("/{user_id}", response_model=schemas.User, dependencies=[Depends(PermissionChecker("user:update"))])
async def update_user(
    user_update: schemas.UserUpdate,
    user: User = Depends(deps.get_user),
    session: AsyncSession = Depends(deps.get_db_session),
):
    role = await session.scalar(select(Role).where(Role.name == user_update.role_name))
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role {user_update.role_name} does not exist"
        )

    if user.name == settings.DEFAULT_ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gebruiker '{user.name}' kan niet worden gewijzigd"
        )

    partner_organization = (
        await deps.get_partner_organization(user_update.partner_organization_name, session)
        if user_update.partner_organization_name
        else None
    )

    expected_role: RoleNames = "partner"
    if partner_organization is not None and user_update.role_name != expected_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Een partnerorganisatie kan alleen worden toegewezen aan gebruikers met rol {expected_role}",
        )

    user.role = role
    user.partner_organization = partner_organization

    return user


@router.delete("/{user_id}", dependencies=[Depends(PermissionChecker("user:delete"))])
async def delete_user(
    user: User = Depends(deps.get_user),
    session: AsyncSession = Depends(deps.get_db_session),
):
    if user.name == settings.DEFAULT_ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gebruiker '{user.name}' kan niet worden verwijderd"
        )

    await session.delete(user)

    keycloak_user = keycloak_service.get_user(user.name)
    if not keycloak_user:
        logger.warning(f"Keycloak user {user.name} not found, skipping deletion")
    else:
        keycloak_service.delete_user(user.name)

    return


@router.post(
    "/{user_id}/reset-password",
    response_model=schemas.UserPasswordUpdate,
    dependencies=[Depends(PermissionChecker("user:update"))],
)
async def reset_password(
    user: User = Depends(deps.get_user),
):
    new_password = keycloak_service.set_password(user.name, password_is_temporary=True)
    return schemas.UserPasswordUpdate(password=new_password)
