from sqlalchemy.ext.asyncio import AsyncSession

import app.core.models as models
from app.schemas.partner_organization import PartnerOrganizationUpsert

from .product import get_products_by_names


async def upsert_partner_organization(
    partner_organization_upsert: PartnerOrganizationUpsert,
    partner_organization: models.PartnerOrganization,
    session: AsyncSession,
):
    partner_organization.name = partner_organization_upsert.name
    partner_organization.description = partner_organization_upsert.description
    partner_organization.description_short = partner_organization_upsert.description_short
    products = await get_products_by_names(partner_organization_upsert.product_names, session=session)
    partner_organization.products = products
