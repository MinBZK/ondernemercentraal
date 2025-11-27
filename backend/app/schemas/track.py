from __future__ import annotations

import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from app.core.models.track import TrackStatus
from app.core.types import FileType, TrackPriority, TrackTypes

from .base import BaseSchema
from .form_data import FormData
from .form_template import RequiredFormTemplate


class TrackCreate(BaseModel):
    track_type_name: TrackTypes
    partner_organization_name: str | None
    priority: TrackPriority | None = None
    product_name: str | None = None
    product_category_name: str | None = None
    status: TrackStatus | None = None
    completion_cause: str | None
    completion_approved: bool = False

    @model_validator(mode="after")
    def validate_new_track(self) -> Self:
        if self.track_type_name == "SHVO" and self.priority is None:
            raise ValueError(f"Priority must be set for '{self.track_type_name}' track type.")

        return self


class TrackBase(BaseSchema, TrackCreate):
    start_dt: datetime.datetime | None
    end_dt: datetime.datetime | None
    required_forms: list[RequiredFormTemplate]
    forms: list[FormData]
    required_file_types: list[FileType]
    case_id: UUID


class Track(TrackBase):
    case: "CaseBase"
    appointments: list["AppointmentBase"]
    case_number: int
    client_initials: str
    client_last_name: str
    client_residence_location: str
    client_phone_number: str | None
    client_email: str


class TrackUpdate(TrackCreate):
    pass


from .case import CaseBase  # noqa: E402, I001
from .appointment import AppointmentBase  # noqa: E402


Track.model_rebuild()
