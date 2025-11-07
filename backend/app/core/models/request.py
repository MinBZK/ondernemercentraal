from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from uuid import UUID

from sqlalchemy import VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.types import FormNames
from app.schemas.form_template import RequiredFormTemplate

from .base_model import BaseModel

if TYPE_CHECKING:
    from .case import Case
    from .form_data import FormData


RequestName = Literal["IOAZ-aanvraag", "BBZ-aanvraag", "BBZ-verlenging-aanvraag"]


class Request(BaseModel):
    __tablename__ = "request"

    name: Mapped[RequestName] = mapped_column(VARCHAR(256), nullable=False)
    case: Mapped[Case] = relationship("Case", back_populates="requests")
    case_id: Mapped[UUID] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"), nullable=False)

    forms: Mapped[list[FormData]] = relationship("FormData", back_populates="request", lazy="joined")

    @property
    def form(self):
        """
        Returns the first form associated with this request.
        """
        assert len(self.forms) == 1, "There should be at least and at most one form associated with a request."
        if self.forms:
            return self.forms[0]

    @property
    def required_forms(self):
        allowed_form_names: list[FormNames] = ["BBZ-aanvraag", "BBZ-verlenging-aanvraag", "IOAZ-aanvraag"]
        return [RequiredFormTemplate(name=f) for f in allowed_form_names]

    @property
    def form_is_completed(self):
        return self.form is not None and self.form.has_valid_payload

    @property
    def form_status(self):
        assert self.form
        return self.form.status
