from pydantic import BaseModel

from .base import BaseSchema


class PartnerOrganizationUpsert(BaseModel):
    name: str
    product_names: list[str]
    description: str | None
    description_short: str | None


class PartnerOrganization(PartnerOrganizationUpsert, BaseSchema):
    product_category_names: set[str]
