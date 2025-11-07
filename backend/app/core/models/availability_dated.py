from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.schemas.availability import AvailabilityDefined

from .base_model import BaseModel

if TYPE_CHECKING:
    from .availability_slot_defined import AvailabilitySlotDefined


class AvailabilityDated(BaseModel):
    __tablename__ = "availability_dated"

    default: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True, unique=True, default=None)

    _availability_slots_defined: Mapped[list[AvailabilitySlotDefined]] = relationship(
        "AvailabilitySlotDefined",
        back_populates="availability_dated",
        cascade="all, delete-orphan",
    )

    @property
    def availability_slots_defined(self):
        """
        Returns the availability in a flat format, without cumbersome nested relationships.
        """
        return [
            AvailabilityDefined(
                hour_start=slot.availability_slot.hour_start,
                hour_end=slot.availability_slot.hour_end,
                capacity=slot.capacity,
            )
            for slot in self._availability_slots_defined
        ]

    def __repr__(self) -> str:
        return f"<AvailabilityDated(id={self.id}, default={self.default}, date={self.date})>"
