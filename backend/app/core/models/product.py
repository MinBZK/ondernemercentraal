from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .product_category import ProductCategory
    from .track import Track


class Product(BaseModel):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True, unique=False)
    product_category_id: Mapped[UUID] = mapped_column(
        ForeignKey("product_category.id", ondelete="CASCADE"), nullable=False
    )
    product_category: Mapped[ProductCategory] = relationship("ProductCategory", lazy="joined")
    tracks: Mapped[list[Track]] = relationship("Track", lazy="joined")

    @property
    def product_category_name(self):
        return self.product_category.name
