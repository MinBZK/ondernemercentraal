import datetime

from pydantic import BaseModel

from .base import BaseSchema


class AvailabilitySlot(BaseSchema):
    hour_start: int
    hour_end: int


class AvailabilitySlotDefined(BaseSchema):
    availability_slot: AvailabilitySlot
    capacity: int


class AvailabilityDefined(BaseModel):
    """
    A simplified, flat model of the availability.
    """

    hour_start: int
    hour_end: int
    capacity: int


class AvailabilityDated(BaseSchema):
    default: bool
    date: datetime.date | None
    availability_slots_defined: list[AvailabilityDefined]


class AvailabilityResponse(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    availability_defined_dated: list[AvailabilityDated]
    availability_defined_default: AvailabilityDated
