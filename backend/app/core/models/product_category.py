from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .product import Product
    from .track import Track


class ProductCategory(BaseModel):
    __tablename__ = "product_category"

    name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)

    products: Mapped[list[Product]] = relationship(
        "Product", back_populates="product_category", cascade="all, delete-orphan"
    )

    tracks: Mapped[list[Track]] = relationship("Track", lazy="joined")
