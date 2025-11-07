from app.core.types import RoleNames

from .base import BaseSchema


class Role(BaseSchema):
    name: RoleNames
