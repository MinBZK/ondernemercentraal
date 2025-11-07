from __future__ import annotations

from pydantic import BaseModel

from app.core.models.request import RequestName
from app.core.types import FormStatus

from .base import BaseSchema
from .form_data import FormData


class RequestCreate(BaseModel):
    name: RequestName


class RequestUpsert(RequestCreate):
    pass


class Request(BaseSchema, RequestUpsert):
    form: FormData
    form_is_completed: bool
    form_status: FormStatus
