from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import RoleNames

from .base_model import BaseModel


class Role(BaseModel):
    __tablename__ = "role"

    name: Mapped[RoleNames] = mapped_column(VARCHAR(256), nullable=False, unique=True)
