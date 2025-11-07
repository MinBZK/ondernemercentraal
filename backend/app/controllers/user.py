from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.middleware.dependencies as deps
import app.schemas.user as schemas
from app.core.models import Role, User
from app.core.services import keycloak_service
from app.core.types import RoleNames


async def create_user(session: AsyncSession, user_new: schemas.UserCreate, password_override: str | None = None):
    role = await session.scalar(select(Role).where(Role.name == user_new.role_name))
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role {user_new.role_name} does not exist")

    user = await session.scalar(select(User).where(User.name == user_new.name))
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gebruiker '{user_new.name}' bestaat al")

    partner_organization = (
        await deps.get_partner_organization(user_new.partner_organization_name, session)
        if user_new.partner_organization_name
        else None
    )

    expected_role: RoleNames = "partner"
    if partner_organization is not None and user_new.role_name != expected_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Een partner kan alleen worden toegewezen aan gebruikers met rol {expected_role}",
        )

    created_user = User(name=user_new.name, role=role, partner_organization=partner_organization, active=True)
    session.add(created_user)

    credentials = keycloak_service.upsert_user(username=user_new.name, password_override=password_override)

    return credentials, created_user
