from pydantic import BaseModel, computed_field

from app.config import form_permission_mapping
from app.config.permissions import Permissions
from app.core.types import FormNames

from .base import BaseSchema


class FormTemplate(BaseSchema):
    name: FormNames
    template_schema: dict


class RequiredFormTemplate(BaseModel):
    name: FormNames

    @computed_field
    @property
    def required_permission(self) -> Permissions:
        return form_permission_mapping[self.name]
