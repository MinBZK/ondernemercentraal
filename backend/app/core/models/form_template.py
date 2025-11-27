import json

from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.config import form_permission_mapping, form_schemas
from app.core.types import FormNames

from .base_model import BaseModel
from .payload_validation import PayloadValidation


class FormTemplate(BaseModel):
    __tablename__ = "form_template"

    name: Mapped[FormNames] = mapped_column(VARCHAR(256), nullable=False, unique=True)

    @property
    def template_schema(self):
        assert self.name in form_schemas.keys(), f"Form schema for '{self.name}' not found in form_schemas"
        with open(form_schemas[self.name], "r") as f:
            schema = json.load(f)
        return schema

    def get_payload_validation(self, payload: dict):
        return PayloadValidation(jsonschema=self.template_schema, payload=payload)

    @property
    def required_permission(self):
        return form_permission_mapping[self.name]
