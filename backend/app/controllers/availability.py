import datetime
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.models import Appointment, AvailabilityDated, AvailabilitySlotDefined
from app.core.types import AppointmentTypeName


@dataclass
class AppointmentSlot:
    start_time: datetime.datetime
    end_time: datetime.datetime


@dataclass
class AppointmentSlotWithCapacityAndUtilization(AppointmentSlot):
    appointments: list[Appointment]
    availability_slots_defined_dated: list[AvailabilityDated]
    availability_slots_defined_default: AvailabilityDated

    @property
    def __slots_defined_by_date(self):
        return {slot.date: slot for slot in self.availability_slots_defined_dated}

    @property
    def utilization(self):
        """
        Returns the utilization of the appointment slot.
        """
        # Find the appointments that overlap with the appointment slot.
        target_appointment_type: AppointmentTypeName = "Checkgesprek"
        overlapping_appointments = [
            ap
            for ap in self.appointments
            if (
                ap.start_time is not None
                and ap.end_time is not None
                and ap.start_time < self.end_time
                and ap.end_time > self.start_time
                and ap.appointment_type.name == target_appointment_type
            )
        ]

        return len(overlapping_appointments)

    @property
    def capacity(self):
        """
        Returns the capacity of the appointment slot.
        """

        # Find all the slots, because dated slots can be defined only for some slots
        slots_defined_default = self.availability_slots_defined_default.availability_slots_defined

        availability_slots_defined_dated = self.__slots_defined_by_date.get(self.start_time.date(), None)
        if availability_slots_defined_dated:
            slots_defined_dated = availability_slots_defined_dated.availability_slots_defined
        else:
            slots_defined_dated = None

        # Find the availability slot for the appointment slot from the dated slots first.
        availability_slot_from_dated = (
            next(
                (
                    slot
                    for slot in slots_defined_dated
                    if slot.hour_start <= self.start_time.hour and slot.hour_end >= self.end_time.hour
                ),
                None,
            )
            if slots_defined_dated
            else None
        )

        # Find the availability based on the default of slots.
        availability_slot_from_default = next(
            (
                slot
                for slot in slots_defined_default
                if slot.hour_start <= self.start_time.hour and slot.hour_end >= self.end_time.hour
            ),
            None,
        )

        # If there is no dated availability, use the default availability.
        availability_slot = availability_slot_from_dated or availability_slot_from_default
        assert availability_slot, "No availability slot found for the given appointment slot."

        return availability_slot.capacity

    @property
    def has_advisor_available(self):
        return self.utilization < self.capacity


@dataclass
class AvailabilityData:
    appointments: list[Appointment]
    availability_slots_defined_dated: list[AvailabilityDated]
    availability_slots_defined_default: AvailabilityDated


async def get_availability_data(session: AsyncSession, start_date: datetime.date, end_date: datetime.date):
    """
    Returns data required for availability:
    - Appointments
    - Availability slots defined for the given date range
    - Default availability slots defined
    """
    query = select(Appointment).where(
        Appointment.start_time >= start_date, Appointment.start_time < end_date + datetime.timedelta(days=1)
    )
    appointments = list((await session.scalars(query)).unique().all())
    query_base = select(AvailabilityDated).options(
        joinedload(AvailabilityDated._availability_slots_defined).joinedload(AvailabilitySlotDefined.availability_slot)
    )
    query_dated = query_base.where(AvailabilityDated.date.between(start_date, end_date))
    query_default = query_base.where(AvailabilityDated.default.is_(True))
    slots_defined_dated = list((await session.scalars(query_dated)).unique())
    slots_defined_default = await session.scalar(query_default)
    assert slots_defined_default
    return AvailabilityData(
        appointments=appointments,
        availability_slots_defined_dated=slots_defined_dated,
        availability_slots_defined_default=slots_defined_default,
    )
