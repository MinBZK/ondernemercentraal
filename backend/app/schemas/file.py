from pydantic import BaseModel

from app.core.types import FileType

from .base import BaseSchema


class FileUpdate(BaseModel):
    description: str | None
    approved: bool
    file_type: FileType


class FileBase(BaseSchema, FileUpdate):
    filename: str
    approval_required: bool
