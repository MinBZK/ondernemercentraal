from __future__ import annotations

from pydantic import Field, computed_field

from .appointment import AppointmentPublic
from .base import BaseSchema
from .user import UserBase


class CaseBase(BaseSchema):
    description: str


class CaseWithClientAndAdvisor(CaseBase):
    client: "Client"
    client_with_user: "ClientInternal" = Field(alias="client")
    case_number: int
    client_bsn: str
    client_last_name: str
    client_initials: str
    advisor: UserBase | None
    advisor_name: str | None
    is_active: bool

    @computed_field
    @property
    def client_company_name(self) -> str | None:
        return self.client.company_name

    @computed_field
    @property
    def client_email(self) -> str:
        return self.client.email


class CasePublic(CaseBase):
    initial_appointment: AppointmentPublic | None


class Case(CaseWithClientAndAdvisor):
    advisor: UserBase | None
    advisor_name: str | None
    is_active: bool


# ruff: noqa: I001, I002
from .client import Client, ClientInternal  # noqa: E402


# CaseWithRelations.model_rebuild()
Case.model_rebuild()
