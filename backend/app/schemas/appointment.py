import datetime
from uuid import UUID

from pydantic import BaseModel, Field, computed_field, model_validator
from typing_extensions import Self

from app.core.types import AppointmentStatus, AppointmentTypeName

from .base import BaseSchema
from .form_data import FormData
from .form_template import RequiredFormTemplate
from .track import TrackBase


class AppointmentSlot(BaseSchema):
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None


class AppintmentSlotWithAvailability(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    has_advisor_available: bool


class AppointmentType(BaseModel):
    name: AppointmentTypeName


class AppointmentPublic(AppointmentSlot, BaseSchema):
    appointment_type: AppointmentType = Field(exclude=True)

    @computed_field
    @property
    def appointment_type_name(self) -> AppointmentTypeName:
        return self.appointment_type.name


class AppointmentBase(AppointmentPublic):
    forms: list[FormData]
    partner_organization_name: str | None
    status: AppointmentStatus
    required_forms: list[RequiredFormTemplate]
    track: TrackBase | None
    case_id: UUID


class Appointment(AppointmentBase):
    case_number: int
    client_initials: str
    client_last_name: str
    client_residence_location: str
    client_phone_number: str | None
    client_email: str


class AppointmentNew(BaseModel):
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None
    appointment_type_name: AppointmentTypeName
    partner_organization_name: str | None
    status: AppointmentStatus

    @model_validator(mode="after")
    def validate_appointment(self) -> Self:
        if (self.start_time is None and self.end_time is not None) or (
            self.start_time is not None and self.end_time is None
        ):
            raise ValueError("Both start_time and end_time must be provided.")

        return self


class AppointmentUpdate(AppointmentNew):
    pass
