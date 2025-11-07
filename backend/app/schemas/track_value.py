from pydantic import BaseModel

from .base import BaseSchema


class PartnerOrganizationCreate(BaseModel):
    name: str
    product_names: list[str]


class PartnerOrganization(BaseSchema, PartnerOrganizationCreate):
    pass


class TrackTypeCreate(BaseModel):
    name: str


class TrackType(BaseSchema, PartnerOrganizationCreate):
    pass
