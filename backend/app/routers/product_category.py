from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.core.models as models
import app.middleware.dependencies as deps
import app.schemas.product as schemas
from app.middleware.permissions import PermissionChecker

router = APIRouter(prefix="/product-category", tags=["product category"])


@router.get(
    "/",
    response_model=list[schemas.ProductCategory],
    dependencies=[Depends(PermissionChecker("product-category:read"))],
)
async def get_cases(
    session: AsyncSession = Depends(deps.get_db_session),
):
    return list(
        (
            await session.scalars(select(models.ProductCategory).options(joinedload(models.ProductCategory.products)))
        ).unique()
    )


@router.post("/", dependencies=[Depends(PermissionChecker("product-category:create"))])
async def create_product_category(
    product_category_new: schemas.ProductCategoryCreate,
    session: AsyncSession = Depends(deps.get_db_session),
):
    existing_product_category = await session.scalar(
        select(models.ProductCategory).where(models.ProductCategory.name == product_category_new.name)
    )
    if existing_product_category is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Pijler '{product_category_new.name}' bestaat al"
        )

    product_category = models.ProductCategory(name=product_category_new.name)
    session.add(product_category)
    return


@router.put("/{product_category_id}", dependencies=[Depends(PermissionChecker("product-category:update"))])
async def update_product_category(
    product_category_update: schemas.ProductCategoryUpdate,
    product_category: models.ProductCategory = Depends(deps.get_product_category),
):
    product_category.name = product_category_update.name
    return


@router.delete("/{product_category_id}", dependencies=[Depends(PermissionChecker("product-category:delete"))])
async def delete_product_category(
    product_category: models.ProductCategory = Depends(deps.get_product_category),
    session: AsyncSession = Depends(deps.get_db_session),
):
    if len(product_category.products) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pijler '{product_category.name}' kan niet verwijderd worden omdat er dienstverleningen aan gekoppeld zijn.",  # noqa: E501
        )
    await session.delete(product_category)
    return
