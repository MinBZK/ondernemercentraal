import datetime
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.availability import (
    AppointmentSlot,
    AppointmentSlotWithCapacityAndUtilization,
    get_availability_data,
)
from app.core.models import Appointment, AvailabilityDated
from app.middleware.dependencies import get_db_session
from app.schemas.appointment import AppintmentSlotWithAvailability as AppointmentSlotSchema

router = APIRouter(prefix="/appointment-slot", tags=["appointment"])


@dataclass
class AppointmentScheduler:
    start_date: datetime.date
    end_date: datetime.date
    appointments: list[Appointment]
    availability_slots_defined_dated: list[AvailabilityDated]
    availability_slots_defined_default: AvailabilityDated

    @property
    def slots_defined_by_date(self):
        """
        A dictionary of availability slots defined by date.
        """
        return {slot.date: slot for slot in self.availability_slots_defined_dated}

    @property
    def potential_dates_in_scope(self):
        """
        Returns all dates between the start and end date.
        """
        all_dates = [
            self.start_date + datetime.timedelta(days=i) for i in range((self.end_date - self.start_date).days)
        ]
        return [d for d in all_dates if d.weekday() not in (5, 6)]  # Exclude weekends (Saturday and Sunday)

    @property
    def appointment_slots(self):
        """
        Generates appointment slots based on the start_date and end_date and default availability slots.
        The capacity is not taken into account, this only matches the availability and appointment slots.

        Note: an availability slot can have a wider scope than appointment slot.
        - An availability slot can be defined from 9-12
        - An appointment slot can be defined from 9-10, 10-11, etc.
        """
        slots: list[AppointmentSlotWithCapacityAndUtilization] = []

        availability_slots = [s for s in self.availability_slots_defined_default.availability_slots_defined]
        for date in self.potential_dates_in_scope:
            for av_slot in availability_slots:
                # Generate the available appointment slots based on the start and end of the availability slot.
                def generate_appointment_slot_intervals(start: int, end: int):
                    return tuple((i - 1, i) for i in range(start + 1, end + 1))

                appointment_slot_intervals = generate_appointment_slot_intervals(
                    start=av_slot.hour_start, end=av_slot.hour_end
                )

                for ap_interval in appointment_slot_intervals:
                    current_time = datetime.datetime.now(tz=ZoneInfo("Europe/Amsterdam"))
                    slot_start_time = datetime.datetime(
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        hour=ap_interval[0],
                        tzinfo=ZoneInfo("Europe/Amsterdam"),
                    )

                    # Don't add slots that do not start in the future
                    if current_time > slot_start_time:
                        continue

                    slots.append(
                        AppointmentSlotWithCapacityAndUtilization(
                            start_time=datetime.datetime(
                                year=date.year,
                                month=date.month,
                                day=date.day,
                                hour=ap_interval[0],
                                tzinfo=ZoneInfo("Europe/Amsterdam"),
                            ),
                            end_time=datetime.datetime(
                                year=date.year,
                                month=date.month,
                                day=date.day,
                                hour=ap_interval[1],
                                tzinfo=ZoneInfo("Europe/Amsterdam"),
                            ),
                            appointments=self.appointments,
                            availability_slots_defined_dated=self.availability_slots_defined_dated,
                            availability_slots_defined_default=self.availability_slots_defined_default,
                        )
                    )

        return slots

    def get_available_capacity_for_appointment_slot(self, appointment_slot: AppointmentSlot):
        """
        Returns the capacity of the appointment slot.

        First, it checks if there is dated availability defined.
        If not, it uses the default availability.
        """
        # Find the availability for the date of the appointment slot. If there is no dated availability,
        # use the default availability.
        availability_slots_defined_dated = self.slots_defined_by_date.get(appointment_slot.start_time.date(), None)
        if not availability_slots_defined_dated:
            availability = self.availability_slots_defined_default
        else:
            availability = availability_slots_defined_dated

        # Find the availability slot for the appointment slot.
        availability_slot = next(
            (
                slot
                for slot in availability.availability_slots_defined
                if slot.hour_start <= appointment_slot.start_time.hour
                and slot.hour_end >= appointment_slot.end_time.hour
            ),
            None,
        )
        assert availability_slot
        return availability_slot.capacity

    def get_utilization_for_appointment_slot(self, appointment_slot: AppointmentSlot):
        """
        Returns the utilization of the appointment slot by checking
        how many appointments overlap with the appointment slot.
        """
        # Find the appointments that overlap with the appointment slot.
        overlapping_appointments = [
            ap
            for ap in self.appointments
            if (
                ap.start_time is not None
                and ap.end_time is not None
                and ap.start_time < appointment_slot.end_time
                and ap.end_time > appointment_slot.start_time
            )
        ]
        return len(overlapping_appointments)


@router.get("/", response_model=list[AppointmentSlotSchema])
async def get_available_slots(
    start_date: datetime.date,
    end_date: datetime.date,
    session: AsyncSession = Depends(get_db_session),
):
    availability_data = await get_availability_data(session, start_date, end_date)
    scheduler = AppointmentScheduler(
        start_date=start_date,
        end_date=end_date,
        appointments=availability_data.appointments,
        availability_slots_defined_dated=availability_data.availability_slots_defined_dated,
        availability_slots_defined_default=availability_data.availability_slots_defined_default,
    )
    return [s for s in scheduler.appointment_slots if s.has_advisor_available]
