from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base_model import BaseModel


class AvailabilitySlot(BaseModel):
    __tablename__ = "availability_slot"

    hour_start: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    hour_end: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    __table_args__ = (UniqueConstraint("hour_start", "hour_end", name="uq_hour_start_hour_end"),)
