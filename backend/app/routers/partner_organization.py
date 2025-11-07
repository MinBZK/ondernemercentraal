from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.controllers.partner_organization as partner_org_controller
import app.core.models as models
import app.middleware.dependencies as deps
from app.middleware.permissions import PermissionChecker
from app.schemas.partner_organization import PartnerOrganization, PartnerOrganizationUpsert

router = APIRouter(prefix="/partner-organization", tags=["partner organization"])


@router.get(
    "/",
    response_model=list[PartnerOrganization],
    dependencies=[Depends(PermissionChecker("partner-organization:read"))],
)
async def fetch_partner_organizations(
    session: AsyncSession = Depends(deps.get_db_session),
):
    query = select(models.PartnerOrganization).options(joinedload(models.PartnerOrganization.products))
    partner_organizations = list((await session.scalars(query)).unique().all())
    return partner_organizations


@router.put("/{partner_organization_id}", dependencies=[Depends(PermissionChecker("partner-organization:update"))])
async def update_partner_organization(
    partner_organization_payload: PartnerOrganizationUpsert,
    partner_organization: models.PartnerOrganization = Depends(deps.get_partner_organization_by_id),
    session: AsyncSession = Depends(deps.get_db_session),
):
    await partner_org_controller.upsert_partner_organization(
        partner_organization_payload, partner_organization, session
    )


@router.post("/", dependencies=[Depends(PermissionChecker("partner-organization:update"))])
async def create_partner_organization(
    partner_organization_payload: PartnerOrganizationUpsert,
    session: AsyncSession = Depends(deps.get_db_session),
):
    partner_organization = models.PartnerOrganization()

    await partner_org_controller.upsert_partner_organization(
        partner_organization_payload, partner_organization, session
    )
    session.add(partner_organization)


@router.delete("/{partner_organization_id}", dependencies=[Depends(PermissionChecker("partner-organization:delete"))])
async def delete_partner_organization(
    partner_organization: models.PartnerOrganization = Depends(deps.get_partner_organization_by_id),
    session: AsyncSession = Depends(deps.get_db_session),
):
    await session.delete(partner_organization)
    return
