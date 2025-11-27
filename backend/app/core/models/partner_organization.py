from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import VARCHAR, Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models import BaseModel

if TYPE_CHECKING:
    from .appointment import Appointment
    from .product import Product
    from .track import Track

partner_organization_product_table = Table(
    "partner_organization_product",
    BaseModel.metadata,
    Column("product_organization_id", ForeignKey("partner_organization.id", ondelete="CASCADE")),
    Column("product_id", ForeignKey("product.id", ondelete="CASCADE")),
)


class PartnerOrganization(BaseModel):
    __tablename__ = "partner_organization"

    name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)

    email: Mapped[str] = mapped_column(VARCHAR(256), nullable=True, unique=False)

    description: Mapped[str | None] = mapped_column(VARCHAR(4096), nullable=True, unique=False)
    description_short: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True, unique=False)

    tracks: Mapped[list[Track]] = relationship(
        "Track",
        back_populates="partner_organization",
    )

    appointments: Mapped[list[Appointment]] = relationship(
        "Appointment",
        back_populates="_partner_organization",
    )

    products: Mapped[list["Product"]] = relationship(secondary=partner_organization_product_table, lazy="joined")

    @property
    def product_names(self):
        return [product.name for product in self.products]

    @property
    def product_categories(self):
        all_product_categories = [p.product_category for p in self.products]
        all_product_category_ids = set([pc.id for pc in all_product_categories])
        return [next(pc for pc in all_product_categories if pc.id == pc_id) for pc_id in all_product_category_ids]

    @property
    def product_category_names(self):
        return {pc.name for pc in self.product_categories}

    # @property
    # def __partner_organization_config(self):
    #     partner_org = next((p for p in partner_organizations if p["organisatie_naam"] == self.name), None)
    #     assert partner_org, "Partner organization configuration not found for: {}".format(self.name)
    #     return partner_org

    # @property
    # def products(self):
    #     return self.__partner_organization_config["products"]

    # @property
    # def description(self):
    #     return self.__partner_organization_config["description"]

    # @property
    # def description_short(self):
    #     return self.__partner_organization_config["description_short"]
