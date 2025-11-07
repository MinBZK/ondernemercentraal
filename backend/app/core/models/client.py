from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import VARCHAR, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .case import Case
    from .user import User


class Client(BaseModel):
    __tablename__ = "client"

    initials: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    last_name_prefix: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    company_location: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    residence_location: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    company_name: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=False)
    kvk_number: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True)
    bsn: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    phone_number: Mapped[str] = mapped_column(VARCHAR(256), nullable=False)
    agree_to_share_data: Mapped[bool] = mapped_column(Boolean, nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)
    email_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False)

    cases: Mapped[list[Case]] = relationship(
        "Case", back_populates="client", cascade="all, delete-orphan", lazy="selectin"
    )

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    user: Mapped[User | None] = relationship(
        "User",
        back_populates="client",
    )

    @property
    def active_case(self):
        active_cases = [case for case in self.cases if case.is_active is not None]
        assert len(active_cases) <= 1, "Client should have at most one active case"
        if len(active_cases) > 0:
            return active_cases[0]

    @property
    def written_name(self):
        return f"{self.initials} {self.last_name_prefix or ''} {self.last_name}".strip()
