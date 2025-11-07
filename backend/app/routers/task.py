import datetime as dt
from enum import Enum
from typing import Any, TypedDict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.middleware.dependencies as deps
import app.schemas.task as schemas
from app.config.permissions import Permissions
from app.core.models import Case, Task, User
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker
from app.util.misc import format_datetime

router = APIRouter(prefix="/task", tags=["Task"])


def validate_permission(user: User, permission: Permissions, new_value: Any, old_value: Any):
    value_has_updated = new_value != old_value
    if not user.has_permission(permission) and value_has_updated:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def upsert_task(
    task: Task,
    payload: schemas.TaskUpsert,
    user: User,
    session: AsyncSession,
    email_notifier: EmailNotifier,
):
    case = await deps.get_case(case_id=payload.case_id, user=user, session=session)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if payload.user_id:
        assigned_user = await session.scalar(select(User).where(User.id == payload.user_id))
        if not assigned_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    else:
        assigned_user = None

    task_belongs_to_user = task.user_id == user.id
    if (user.has_role("partner") or user.has_role("ondernemer")) and not task_belongs_to_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
        )

    old_assigned_user = task.user
    new_assigned_user = assigned_user

    if new_assigned_user and not case.is_linked_to_user(new_assigned_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user is not linked to the case")

    if task.status != payload.status:
        validate_permission(user, "task:update", payload.status, task.status)
        task.status = payload.status

    if task.description != payload.description:
        validate_permission(user, "task:update", payload.description, task.description)
        task.description = payload.description

    if task.due_date != payload.due_date:
        validate_permission(user, "task:update", payload.due_date, task.due_date)
        task.due_date = payload.due_date

    if task.user != assigned_user:
        validate_permission(user, "task:update", payload.user_id, task.user_id)
        task.user = assigned_user

    if task.case_id != case.id:
        validate_permission(user, "task:update", payload.case_id, task.case_id)
        task.case = case

    if task.completed != payload.completed:
        validate_permission(user, "task:update:completion-status", payload.completed, task.completed)
        task.completed = payload.completed

    old_assigned_user_id = old_assigned_user.id if old_assigned_user else None
    new_assigned_user_id = new_assigned_user.id if new_assigned_user else None

    removed_user = old_assigned_user if old_assigned_user_id != new_assigned_user_id and old_assigned_user else None

    newly_assigned_user = (
        new_assigned_user if new_assigned_user_id != old_assigned_user_id and new_assigned_user else None
    )

    if removed_user:
        email_notifier.notify_user(
            user=removed_user,
            content=["Je bent niet meer toegewezen aan deze taak.", "Omschrijving:", task.description],
            subject="Toewijzing aan taak verwijderd",
        )

    if newly_assigned_user:
        email_notifier.notify_user(
            user=newly_assigned_user,
            content=["Je bent toegewezen aan een nieuwe taak.", "Omschrijving:", task.description],
            subject="Je hebt een taak toegewezen gekregen",
        )

    return task


@router.get("/", response_model=list[schemas.Task], dependencies=[Depends(PermissionChecker("task:read"))])
async def get_tasks(
    case: Case = Depends(deps.get_optional_case),
    session: AsyncSession = Depends(deps.get_db_session),
    user: User = Depends(deps.get_logged_in_user),
):
    query = select(Task).options(joinedload(Task.case), joinedload(Task.user))
    if case:
        query = query.where(Task.case_id == case.id)

    tasks = list((await session.scalars(query)).unique())

    if user.has_role("partner") or user.has_role("ondernemer"):
        tasks = [task for task in tasks if task.user_id == user.id]

    return tasks


class TaskMutation(TypedDict):
    old_value: str
    new_value: str


def stringify_value(value: Any) -> str:
    if isinstance(value, Enum):
        return value.value
    elif isinstance(value, dt.datetime):
        return format_datetime(value)
    else:
        return str(value)


def get_mutations(task: Task, task_update: schemas.TaskUpsert):
    mutations: dict[str, TaskMutation] = {}
    for update_key in task_update.model_dump().keys():
        old_value = stringify_value(getattr(task, update_key))
        new_value = stringify_value(getattr(task_update, update_key))
        if old_value != new_value:
            mutations[update_key] = TaskMutation(old_value=old_value, new_value=new_value)
    return mutations


@router.put("/{task_id}")
async def update_task(
    task_update: schemas.TaskUpsert,
    task: Task = Depends(deps.get_task),
    user: User = Depends(deps.get_logged_in_user),
    session: AsyncSession = Depends(deps.get_db_session),
    email_notifier: EmailNotifier = Depends(EmailNotifier),
):
    mutations = get_mutations(task, task_update)
    await upsert_task(task, task_update, user, session, email_notifier)
    if task.user and len(mutations.keys()) > 0:
        email_notifier.notify_user(
            user=task.user,
            subject="Taak bijgewerkt",
            case=task.case,
            content=[
                "Een aan jou toegewezen taak is gewijzigd. De omschrijving van deze taak is:",
                task.description,
            ],
        )


@router.post("/", dependencies=[Depends(PermissionChecker("task:create"))])
async def create_task(
    task_create: schemas.TaskUpsert,
    user: User = Depends(deps.get_logged_in_user),
    session: AsyncSession = Depends(deps.get_db_session),
    email_notifier: EmailNotifier = Depends(EmailNotifier),
):
    new_task = Task()
    session.add(new_task)
    upserted_task = await upsert_task(new_task, task_create, user, session, email_notifier)
    session.add(upserted_task)
    return


@router.delete("/{task_id}", dependencies=[Depends(PermissionChecker("task:delete"))])
async def delete_task(
    task: User = Depends(deps.get_task),
    session: AsyncSession = Depends(deps.get_db_session),
):
    await session.delete(task)
    return
