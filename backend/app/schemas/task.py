from __future__ import annotations

import datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.models.task import TaskStatus

from .base import BaseSchema
from .user import User


class TaskCreate(BaseModel):
    status: TaskStatus
    description: str
    due_date: datetime.datetime
    case_id: UUID
    user_id: UUID | None
    completed: bool


class TaskUpsert(TaskCreate):
    pass


class TaskBase(BaseSchema, TaskUpsert):
    is_due: bool
    user: User | None
    user_name: str | None


class Task(TaskBase):
    case: "CaseBase"
    case_number: int


from .case import CaseBase  # noqa: E402

CaseBase.model_rebuild()
