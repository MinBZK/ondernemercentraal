from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.core.models as models


async def get_products_by_names(product_names: list[str], session: AsyncSession):
    products = list(
        (await session.scalars(select(models.Product).where(models.Product.name.in_(product_names)))).unique()
    )
    unique_retrieved_product_names = set(p.name for p in products)
    products_not_found = set(product_names) - unique_retrieved_product_names
    assert len(products_not_found) == 0, f"Products not found: {products_not_found}"
    return products
