from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.schemas.case as schemas
from app.controllers import Case as CaseController
from app.controllers.appointment import AppointmentController
from app.controllers.track import TrackController
from app.core.models import Case, User
from app.core.types import RoleNames
from app.middleware.dependencies import get_case, get_db_session, get_email_notifier, get_logged_in_user
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker

router = APIRouter(prefix="/case", tags=["case"])


@router.get(
    "/", response_model=list[schemas.CaseWithClientAndAdvisor], dependencies=[Depends(PermissionChecker("case:read"))]
)
async def get_cases(
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_logged_in_user),
):
    query = CaseController.base_query()
    cases = list((await session.scalars(query)).unique())
    return [c for c in cases if c.is_linked_to_user(user)]


@router.patch("/{case_id}/advisor", dependencies=[Depends(PermissionChecker("case:update"))])
async def update_case_advisor(
    advisor_id: UUID | None = None,
    email_notifier: EmailNotifier = Depends(get_email_notifier),
    case: Case = Depends(get_case),
    user: User = Depends(get_logged_in_user),
    session: AsyncSession = Depends(get_db_session),
):
    if advisor_id:
        advisor = await session.scalar(select(User).where(User.id == advisor_id).options(joinedload(User.role)))
        if not advisor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Advisor not found")
        allowed_roles: list[RoleNames] = ["adviseur", "beheerder"]
        if advisor.role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must have one of the following roles: " + ",".join(allowed_roles),
            )
    else:
        advisor = None

    old_advisor = case.advisor
    new_advisor = advisor
    case.advisor = new_advisor

    if old_advisor is not None and new_advisor != old_advisor and old_advisor.id != user.id:
        email_notifier.notify_user(
            user=old_advisor,
            subject="Toewijzing aan dossier verwijderd",
            content=[f"Gebruiker '{user.name}' heeft jouw toewijzing aan {case.description} verwijderd."],
        )

    if new_advisor is not None and new_advisor != old_advisor and new_advisor.id != user.id:
        email_notifier.notify_user(
            user=new_advisor,
            subject="Dossier toegewezen",
            case=case,
            content=[
                f"Je bent toegewezen aan {case.description} door gebruiker '{user.name}'.",
            ],
        )

    return


@router.get("/{case_id}", response_model=schemas.Case, dependencies=[Depends(PermissionChecker("case:read"))])
async def fetch_case(
    case: Case = Depends(get_case),
    session: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_logged_in_user),
):
    """
    Returns the case with its related tracks, appointments and tasks.
    """

    # Expunge the case and all related objects so that no changes are applied to the database
    session.expunge_all()

    # Only show the tracks and appointments that the user may access
    tracks = await TrackController.get_many(session=session, user=user, case=case)
    appointments = await AppointmentController(session).get_many(user=user, case=case)
    case.tracks = [t for t in tracks if t.case_id == case.id]
    case.appointments = [a for a in appointments if a.case_id == case.id]

    # Only show the tasks that the user may access
    if not user.has_permission("task:read"):
        case.tasks = []

    return case


@router.delete("/{case_id}", dependencies=[Depends(PermissionChecker("case:delete"))])
async def delete_case(
    case: Case = Depends(get_case),
    session: AsyncSession = Depends(get_db_session),
):
    if case.client:
        await session.delete(case.client)
    await session.delete(case)
    return
