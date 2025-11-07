from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.core.types import AppointmentTypeName

from .base_model import BaseModel


class AppointmentType(BaseModel):
    __tablename__ = "appointment_type"

    name: Mapped[AppointmentTypeName] = mapped_column(VARCHAR(256), nullable=False, unique=True)
