from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.models as models
from app.config import partner_organizations
from app.core import settings
from app.core.database import async_session


async def validate_products(session: AsyncSession):
    products = (await session.scalars(select(models.Product))).unique()
    existing_product_names = set([product.name for product in products])
    required_product_names_str = {str(r) for r in settings.REQUIRED_PRODUCT_NAMES}
    missing_product_names = list(required_product_names_str - existing_product_names)
    assert len(missing_product_names) == 0, f"Missing required products: {missing_product_names}"

    # Validate each required product also has partner organizations
    for required_product_name in settings.REQUIRED_PRODUCT_NAMES:
        partner_org = next((p for p in partner_organizations if required_product_name in p["products"]), None)
        assert partner_org, f"Required product '{required_product_name}' does not have a partner organization."


async def main():
    async with async_session.begin() as session:
        await validate_products(session)
