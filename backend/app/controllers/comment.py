from dataclasses import dataclass
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config.permissions import Permissions
from app.core.models import Appointment, Case, Comment, CommentThread, Track, User
from app.middleware.exceptions import NoPermission

MediaTypes = Literal["text/csv", "application/pdf"]
Extensions = Literal[".csv", ".pdf", ".xlsx"]


Actions = Literal["read", "update", "create", "delete"]
Resource = Literal["appointment", "case", "track"]


@dataclass
class CommentController:
    user: User
    session: AsyncSession | None = None
    case: Case | None = None
    track: Track | None = None
    appointment: Appointment | None = None

    def __post_init__(self):
        assert self.case is not None or self.track is not None or self.appointment is not None, (
            "Either case, track or appointment must be provided"
        )

    @property
    def __base_query(self):
        """
        Returns a query that selects files from only the provided case or track.
        """
        query = select(CommentThread).options(joinedload(CommentThread.comments))
        if self.track:
            query = query.where(CommentThread.track_id == self.track.id)
        elif self.case:
            query = query.where(CommentThread.case_id == self.case.id)
        elif self.appointment:
            query = query.where(CommentThread.appointment_id == self.appointment.id)
        else:
            raise NotImplementedError
        return query

    @property
    def _session(self):
        assert self.session
        return self.session

    def __validate_user_permission(self, required_permission: Permissions):
        if not self.user.has_permission(required_permission):
            raise NoPermission(username=self.user.name, required_permission=required_permission)

    async def get_comments(self):
        self.__validate_user_permission("comment:read")
        comment_thread = await self._session.scalar(self.__base_query)
        return comment_thread.comments if comment_thread else []

    async def create_comment(self, content: str):
        self.__validate_user_permission("comment:create")
        comment_thread = await self._session.scalar(self.__base_query)
        if not comment_thread:
            comment_thread = CommentThread(track=self.track, case=self.case, appointment=self.appointment)
            self._session.add(comment_thread)
        comment_thread.comments.append(Comment(created_by_user=self.user, content=content))
