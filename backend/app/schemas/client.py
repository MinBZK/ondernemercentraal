from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, Field

from .base import BaseSchema
from .user import UserWithPermissions


def min_length_if_not_none(value: Any):
    if value is not None and len(value) == 0:
        raise ValueError("Field must be at least 1 character long if not None")


class ClientLocation(BaseModel):
    company_location: str = Field(min_length=1)
    residence_location: str = Field(min_length=1)


class ClientDetails(BaseModel):
    initials: str = Field(min_length=1)
    last_name_prefix: Annotated[str | None, AfterValidator(min_length_if_not_none)] = None
    last_name: str = Field(min_length=1)
    company_name: str | None = Field(min_length=1, default=None)
    kvk_number: str | None = Field(min_length=1, default=None)
    bsn: str = Field(min_length=1)
    phone_number: str = Field(min_length=1)
    agree_to_share_data: bool
    email: str = Field(min_length=1)


class Client(BaseSchema, ClientDetails, ClientLocation):
    pass


class ClientNew(BaseModel):
    location: ClientLocation
    details: ClientDetails


class ClientUpdate(ClientNew):
    pass


class ClientCreateResponse(BaseModel):
    token: str


class ClientWithCasePublic(Client):
    active_case: "CasePublic | None" = None


class ClientInternal(Client):
    user: UserWithPermissions | None


class ClientUpdateResponse(BaseModel):
    message: str | None


from .case import CasePublic  # noqa

ClientWithCasePublic.model_rebuild()
