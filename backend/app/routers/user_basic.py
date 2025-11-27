from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.middleware.dependencies as deps
import app.schemas.user as schemas
from app.core.models import Client, User
from app.middleware.permissions import PermissionChecker

router = APIRouter(prefix="/user-basic", tags=["user"])


@router.get("/", response_model=list[schemas.UserBase], dependencies=[Depends(PermissionChecker("user-basic:read"))])
async def get_users_basic(
    case_id: UUID | None = None,
    session: AsyncSession = Depends(deps.get_db_session),
    user: User = Depends(deps.get_logged_in_user),
):
    """
    Returns a list of users with minimal information, suitable for basic user selection.
    """

    users = list(
        (
            await session.scalars(
                select(User).options(
                    joinedload(User.role),
                    joinedload(User.partner_organization),
                    joinedload(User.client).joinedload(Client.cases),
                )
            )
        ).unique()
    )

    if case_id:
        case = await deps.get_case(user=user, case_id=case_id, session=session)
    else:
        case = None

    relevant_users = []
    if case:
        relevant_users = [u for u in users if case.is_linked_to_user(u)]
    else:
        relevant_users = [u for u in users]

    if user.has_role("partner") or user.has_role("ondernemer"):
        return [u for u in users if u.id == user.id]
    else:
        return relevant_users
