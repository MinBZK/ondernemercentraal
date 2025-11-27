from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, UUID, VARCHAR, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.types import FileType, TrackPriority, TrackStatus, TrackTypes
from app.schemas.form_template import RequiredFormTemplate

from .base_model import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment
    from .case import Case
    from .form_data import FormData
    from .partner_organization import PartnerOrganization
    from .product import Product
    from .product_category import ProductCategory
    from .track_type import TrackType


class Track(BaseModel):
    """
    A track is a procedure handled by external parties.

    Example: ondernemersdienstverlening.
    """

    __tablename__ = "track"

    track_type_id: Mapped[UUID] = mapped_column(ForeignKey("track_type.id", ondelete="CASCADE"), nullable=False)
    track_type: Mapped[TrackType] = relationship("TrackType", lazy="joined")

    case_id: Mapped[UUID] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    case: Mapped[Case] = relationship("Case", back_populates="tracks")

    product_category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("product_category.id", ondelete="SET NULL"), nullable=True
    )
    product_category: Mapped[ProductCategory | None] = relationship(
        "ProductCategory", back_populates="tracks", lazy="joined"
    )

    product_id: Mapped[UUID | None] = mapped_column(ForeignKey("product.id", ondelete="SET NULL"), nullable=True)
    product: Mapped[Product | None] = relationship("Product", back_populates="tracks", lazy="joined")

    partner_organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("partner_organization.id", ondelete="SET NULL"), nullable=True
    )
    partner_organization: Mapped[PartnerOrganization | None] = relationship(
        "PartnerOrganization", back_populates="tracks", lazy="joined"
    )

    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment", back_populates="track", cascade="all, delete-orphan"
    )

    completion_cause: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True)
    completion_approved: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)

    forms: Mapped[list[FormData]] = relationship("FormData", back_populates="track", cascade="all, delete-orphan")

    priority: Mapped[TrackPriority | None] = mapped_column(VARCHAR(256), nullable=True)

    start_dt: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    end_dt: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def track_type_name(self):
        return self.track_type.name

    @property
    def partner_organization_name(self):
        return self.partner_organization.name if self.partner_organization else None

    @property
    def status(self) -> TrackStatus:
        if not self.start_dt:
            return "Nog niet gestart"
        elif not self.end_dt:
            return "Gestart"
        else:
            return "Beëindigd"

    @property
    def required_forms(self):
        return [RequiredFormTemplate(name=f) for f in self.track_type.settings.required_forms]

    @property
    def required_file_types(self):
        required_file_type_mapping: dict[TrackTypes, list[FileType]] = {"SHVO": ["Plan van aanpak"]}
        return required_file_type_mapping.get(self.track_type.name, [])

    @property
    def product_name(self):
        return self.product.name if self.product else None

    @property
    def product_category_name(self):
        return self.product_category.name if self.product_category else None

    @property
    def case_number(self):
        return self.case.case_number

    @property
    def client_initials(self):
        return self.case.client_initials

    @property
    def client_last_name(self):
        return self.case.client_last_name

    @property
    def client_residence_location(self):
        return self.case.client.residence_location

    @property
    def client_phone_number(self):
        return self.case.client.phone_number

    @property
    def client_email(self):
        return self.case.client.email
