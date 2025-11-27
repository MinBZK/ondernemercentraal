from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import app.middleware.dependencies as deps
import app.schemas.track as schemas
from app.controllers import TrackController
from app.core import settings
from app.core.models import Case, PartnerOrganization, Track, User
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker
from app.util.logger import logger

router = APIRouter(tags=["track"])


@router.post("/case/{case_id}/track", dependencies=[Depends(PermissionChecker("track:create"))])
async def create_track(
    track_new: schemas.TrackCreate,
    case: Case = Depends(deps.get_case),
    user: User = Depends(deps.get_logged_in_user),
    session: AsyncSession = Depends(deps.get_db_session),
):
    await TrackController().upsert_track(track=None, track_update=track_new, user=user, session=session, case=case)

    return


@router.get("/track/{track_id}", response_model=schemas.Track, dependencies=[Depends(PermissionChecker("track:read"))])
async def get_track(track: Track = Depends(deps.get_track)):
    return track


@router.delete("/case/{case_id}/track/{track_id}", dependencies=[Depends(PermissionChecker("track:delete"))])
async def delete_track(
    track: Track = Depends(deps.get_track),
    session: AsyncSession = Depends(deps.get_db_session),
):
    await session.delete(track)


@router.put("/case/{case_id}/track/{track_id}")
async def update_track(
    track_update: schemas.TrackUpdate,
    email_notifier: EmailNotifier = Depends(EmailNotifier),
    track: Track = Depends(deps.get_track),
    user: User = Depends(deps.get_logged_in_user),
    session: AsyncSession = Depends(deps.get_db_session),
):
    old_status = track.status
    old_completion_approved = track.completion_approved

    # Permissions are checked in the controller
    await TrackController().upsert_track(track, track_update, user, session)

    # Send email notification if the track status has changed to "Gestart"
    if track_update.status == "Gestart" and old_status != "Gestart":
        if track.partner_organization_name is not None:
            content = [
                f"Ondernemer Centraal heeft voor u traject '{track.track_type_name}' gestart bij '{track.partner_organization_name}'."  # noqa
            ]
        else:
            content = [f"Ondernemer Centraal heeft voor u traject '{track.track_type_name}' gestart."]
        content.append("Er wordt telefonisch contact met u opgenomen.")
        email_notifier.notify_client(
            client=track.case.client,
            content=content,
            subject="Traject gestart",
        )
        if track.partner_organization:
            email_notifier.notify_partner_organization(
                partner_organization=track.partner_organization,
                content=content,
                subject="Traject gestart",
            )

    # Send email notification if the track has been completed
    if track_update.completion_approved and not old_completion_approved:
        if track.partner_organization_name is not None:
            content = [
                f"Ondernemer Centraal heeft voor u traject '{track.track_type_name}' beëindigd bij '{track.partner_organization_name}'."  # noqa
            ]
        else:
            content = [f"Ondernemer Centraal heeft voor u traject '{track.track_type_name}' beëindigd."]
        content.append("Er wordt telefonisch contact met u opgenomen.")
        email_notifier.notify_client(
            client=track.case.client,
            content=content,
            subject="Traject beëindigd",
        )
        if track.partner_organization:
            email_notifier.notify_partner_organization(
                partner_organization=track.partner_organization,
                content=content,
                subject="Traject beëindigd",
            )

    return


@router.get("/track", response_model=list[schemas.Track], dependencies=[Depends(PermissionChecker("track:read"))])
async def get_tracks(
    case: Case = Depends(deps.get_optional_case),
    user: User = Depends(deps.get_logged_in_user),
    session: AsyncSession = Depends(deps.get_db_session),
):
    return await TrackController().get_many(session, user=user, case=case)


@router.patch(
    "/track/{track_id}/partner-organization/{partner_organization_name}",
    response_model=None,
    dependencies=[Depends(PermissionChecker("track:update:partner"))],
)
async def update_track_partner_organization(
    track: Track = Depends(deps.get_track),
    partner_organization: PartnerOrganization = Depends(deps.get_partner_organization),
):
    track.partner_organization = partner_organization
    return


@router.post(
    "/track/{track_id}/partner-organization-choice-request",
    response_model=str,
    dependencies=[Depends(PermissionChecker("track:send-notification:partner-request"))],
)
async def request_partner_organization_choice(
    track: Track = Depends(deps.get_track),
    email_notifier: EmailNotifier = Depends(EmailNotifier),
):
    url = f"{settings.CLIENT_BASE_URL}/beheer/track/{track.id}/partner-organization"
    logger.debug(f"Generated partner organization choice URL: {url}")
    email_notifier.notify_client(
        client=track.case.client,
        content=[
            f"Ondernemer Centraal heeft voor u het traject '{track.track_type_name}' gestart.",
            f"<a href='{url}'>Kies hier een partnerorganisatie die u hierbij kunt gaan helpen.</a>",
        ],
        subject=f"Kies een partnerorganisatie voor traject '{track.track_type_name}'",
    )
    return "Er is een e-mail verstuurd naar de ondernemer met een link om een partnerorganisatie te kiezen."
