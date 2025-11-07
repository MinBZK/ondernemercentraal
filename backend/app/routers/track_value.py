from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import track_completion_causes
from app.core.models import PartnerOrganization, TrackType
from app.core.types import TrackStatus
from app.middleware.dependencies import get_db_session
from app.middleware.permissions import PermissionChecker
from app.schemas.partner_organization import PartnerOrganization as PartnerOrganizationSchema

router = APIRouter(prefix="/track-value", tags=["track"])


class TrackValues(BaseModel):
    track_type: list[str]
    partner_organization: list[PartnerOrganizationSchema]
    completion_causes: list[str]
    status: list[TrackStatus]


@router.get("/", response_model=TrackValues, dependencies=[Depends(PermissionChecker("track:read"))])
async def fetch_track_types(
    session: AsyncSession = Depends(get_db_session),
):
    track_types = list(await session.scalars(select(TrackType)))
    partner_organizations = list((await session.scalars(select(PartnerOrganization))).unique().all())

    return TrackValues(
        track_type=[t.name for t in track_types],
        partner_organization=[PartnerOrganizationSchema.model_validate(p) for p in partner_organizations],
        completion_causes=track_completion_causes,
        status=["Nog niet gestart", "Gestart", "Beëindigd"],
    )
