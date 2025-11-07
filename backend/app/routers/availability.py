import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.schemas.availability as schemas
from app.core.models import AvailabilityDated, AvailabilitySlot, AvailabilitySlotDefined
from app.middleware.dependencies import get_db_session
from app.middleware.permissions import PermissionChecker

router = APIRouter(prefix="/availability", tags=["availability"])


@router.get(
    "/", response_model=schemas.AvailabilityResponse, dependencies=[Depends(PermissionChecker("availability:read"))]
)
async def get_availability(
    start_date: datetime.date,
    end_date: datetime.date,
    session: AsyncSession = Depends(get_db_session),
):
    query = select(AvailabilityDated).options(
        joinedload(AvailabilityDated._availability_slots_defined).joinedload(AvailabilitySlotDefined.availability_slot)
    )
    query_default = query.where(AvailabilityDated.default.is_(True))
    query_dated = query.where(AvailabilityDated.date.between(start_date, end_date))
    slots_defined_dated = list((await session.scalars(query_dated)).unique())
    slot_defined_default = await session.scalar(query_default)

    return schemas.AvailabilityResponse(
        start_date=start_date,
        end_date=end_date,
        availability_defined_dated=[schemas.AvailabilityDated.model_validate(s) for s in slots_defined_dated],
        availability_defined_default=schemas.AvailabilityDated.model_validate(slot_defined_default),
    )


@router.patch("/{date}/slot/{hour_start}", dependencies=[Depends(PermissionChecker("availability:update"))])
async def update_availability(
    date: datetime.date,
    hour_start: int,
    new_capacity: int,
    session: AsyncSession = Depends(get_db_session),
):
    availability_dated = await session.scalar(
        select(AvailabilityDated)
        .where(AvailabilityDated.date == date)
        .options(
            joinedload(AvailabilityDated._availability_slots_defined).joinedload(
                AvailabilitySlotDefined.availability_slot
            )
        )
    )
    if not availability_dated:
        availability_dated = AvailabilityDated(date=date, default=False)
        session.add(availability_dated)
    target_slot = next(
        (s for s in availability_dated._availability_slots_defined if s.availability_slot.hour_start == hour_start),
        None,
    )
    if not target_slot:
        slot = await session.scalar(select(AvailabilitySlot).where(AvailabilitySlot.hour_start == hour_start))
        assert slot
        availability_dated._availability_slots_defined.append(
            AvailabilitySlotDefined(capacity=new_capacity, availability_slot=slot)
        )
    else:
        target_slot.capacity = new_capacity
