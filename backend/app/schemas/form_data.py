from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from app.core.types import FormLinkType, FormNames, FormStatus

from .base import BaseSchema


class FormDataUpsert(BaseModel):
    payload: dict | None


class FormData(BaseSchema, FormDataUpsert):
    payload_unvalidated: dict | None = Field(exclude=True)
    form_template_name: FormNames
    # form_template: FormTemplate
    approval_required: bool
    has_valid_payload: bool
    approved: bool
    submitted: bool
    status: FormStatus
    form_link_type: FormLinkType | None
    case_id: UUID | None
    appointment_id: UUID | None
    track_id: UUID | None
    request_id: UUID | None
    case_description: str | None

    @computed_field
    @property
    def visible_payload(self) -> dict | None:
        return self.payload or self.payload_unvalidated
