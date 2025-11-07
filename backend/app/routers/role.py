from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import app.schemas.role as schemas
from app.core.models import Role
from app.middleware.dependencies import get_db_session
from app.middleware.permissions import PermissionChecker

router = APIRouter(prefix="/role", tags=["role"])


@router.get("/", response_model=list[schemas.Role], dependencies=[Depends(PermissionChecker("role:read"))])
async def get_cases(
    session: AsyncSession = Depends(get_db_session),
):
    return list((await session.scalars(select(Role))).unique())
