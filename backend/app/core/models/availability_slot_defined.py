from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .availability_dated import AvailabilityDated
    from .availability_slot import AvailabilitySlot


class AvailabilitySlotDefined(BaseModel):
    __tablename__ = "availability_slot_defined"

    availability_slot_id: Mapped[UUID] = mapped_column(
        ForeignKey("availability_slot.id", ondelete="CASCADE"), nullable=False
    )
    capacity: Mapped[int] = mapped_column(nullable=False)

    availability_dated: Mapped[AvailabilityDated] = relationship(
        "AvailabilityDated",
        back_populates="_availability_slots_defined",
    )
    availability_dated_id: Mapped[UUID] = mapped_column(
        ForeignKey("availability_dated.id", ondelete="CASCADE"), nullable=False
    )
    availability_slot: Mapped[AvailabilitySlot] = relationship(
        "AvailabilitySlot",
    )

    __table_args__ = (
        UniqueConstraint(
            "availability_slot_id", "availability_dated_id", name="uq_availability_slot_id_availability_dated_id"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AvailabilitySlotDefined(id={self.id}, availability_slot_id={self.availability_slot_id}, "
            f"availability_dated_id={self.availability_dated_id}, capacity={self.capacity})>"
        )
