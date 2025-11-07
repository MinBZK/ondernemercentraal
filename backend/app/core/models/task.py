from __future__ import annotations

import datetime
import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import VARCHAR, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseModel

if TYPE_CHECKING:
    from .case import Case
    from .user import User


class TaskStatus(enum.Enum):
    TO_DO = "Openstaand"
    IN_PROGRESS = "In uitvoering"
    CLOSED = "Gesloten"


class Task(BaseModel):
    __tablename__ = "task"

    description: Mapped[str] = mapped_column(VARCHAR(1024), nullable=False, unique=False)
    due_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.TO_DO)

    case_id: Mapped[UUID] = mapped_column(ForeignKey("case.id", ondelete="CASCADE"), nullable=False)
    case: Mapped[Case] = relationship("Case", back_populates="tasks")

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    user: Mapped[User | None] = relationship("User")

    completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    @property
    def is_due(self):
        return datetime.datetime.now(datetime.timezone.utc) >= self.due_date

    @property
    def user_name(self):
        if self.user is not None:
            return self.user.name

    @property
    def case_number(self):
        if self.case:
            return self.case.case_number
