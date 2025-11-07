from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.core.models as models
import app.middleware.dependencies as deps
import app.schemas.product as schemas
from app.core.settings import settings
from app.middleware.permissions import PermissionChecker

router = APIRouter(prefix="/product", tags=["product"])


async def get_product_category(product_category_name: str, session: AsyncSession):
    query = (
        select(models.ProductCategory)
        .where(models.ProductCategory.name == product_category_name)
        .options(joinedload(models.ProductCategory.products))
    )
    product_category = await session.scalar(query)
    return product_category


@router.get(
    "/",
    response_model=list[schemas.Product],
    dependencies=[Depends(PermissionChecker("product:read"))],
)
async def get_products(
    session: AsyncSession = Depends(deps.get_db_session),
):
    products = await session.scalars(select(models.Product).options(joinedload(models.Product.product_category)))
    return list(products.unique())


@router.post(
    "/",
    dependencies=[Depends(PermissionChecker("product:create"))],
)
async def create_product(
    product_new: schemas.ProductCreate,
    session: AsyncSession = Depends(deps.get_db_session),
):
    product_category = await get_product_category(product_new.product_category_name, session)
    if not product_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product category {product_new.product_category_name} not found",
        )
    product_category.products.append(models.Product(name=product_new.name, code=product_new.code))
    return


@router.put(
    "/{product_id}",
    dependencies=[Depends(PermissionChecker("product:update"))],
)
async def update_product(
    product_update: schemas.ProductUpdate,
    product: models.Product = Depends(deps.get_product),
    session: AsyncSession = Depends(deps.get_db_session),
):
    if product.name in settings.REQUIRED_PRODUCT_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"De dienstverlening '{product.name}' kan niet worden gewijzigd omdat deze verplicht is.",
        )

    product.name = product_update.name
    product.code = product_update.code

    product_category = await get_product_category(product_update.product_category_name, session)
    assert product_category, "Product category not found"
    product.product_category_id = product_category.id
    return


@router.delete(
    "/{product_id}",
    dependencies=[Depends(PermissionChecker("product:delete"))],
)
async def delete_product(
    product: models.Product = Depends(deps.get_product), session: AsyncSession = Depends(deps.get_db_session)
):
    if len(product.tracks) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deze dienstverlening kan niet worden verwijderd omdat deze nog in gebruik is door één of meerdere trajecten.",  # noqa: E501
        )

    if product.name in settings.REQUIRED_PRODUCT_NAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"De dienstverlening '{product.name}' kan niet worden verwijderd omdat deze verplicht is.",
        )

    await session.delete(product)
    return
