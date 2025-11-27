from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import VARCHAR, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.permissions import Permissions, role_permissions
from app.core.types import RoleNames

from .base_model import BaseModel

if TYPE_CHECKING:
    from .case import Case
    from .client import Client
    from .partner_organization import PartnerOrganization
    from .role import Role


class User(BaseModel):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(VARCHAR(256), nullable=False, unique=True)

    cases: Mapped[list[Case]] = relationship(
        "Case",
        back_populates="advisor",
    )

    role_id: Mapped[UUID] = mapped_column(ForeignKey("role.id"), nullable=False)
    role: Mapped[Role] = relationship("Role", lazy="joined")

    partner_organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("partner_organization.id", ondelete="SET NULL"), nullable=True
    )
    partner_organization: Mapped[PartnerOrganization | None] = relationship("PartnerOrganization", lazy="joined")

    client: Mapped[Client | None] = relationship("Client", back_populates="user", lazy="joined")

    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    @property
    def role_name(self):
        return self.role.name

    @property
    def partner_organization_name(self):
        return self.partner_organization.name if self.partner_organization else None

    @property
    def permissions(self):
        return role_permissions.get(self.role_name) or []

    def has_permission(self, required_permission: Permissions):
        """
        Check if the user has the required permission.
        """
        return required_permission in self.permissions

    @property
    def email(self):
        if "@" in self.name:
            return self.name

    @property
    def active_case_id(self):
        if self.client and self.client.active_case:
            return self.client.active_case.id

    def has_role(self, target_role_name: RoleNames):
        return self.role_name == target_role_name
