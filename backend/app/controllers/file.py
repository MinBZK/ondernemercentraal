import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.permissions import Permissions
from app.core.models import Appointment, Case, File, Track, User
from app.core.services import minio_service
from app.core.types import FileType
from app.middleware.email_notification import EmailNotifier
from app.middleware.exceptions import NoPermission
from app.middleware.scan_file import scan_file_for_malware
from app.schemas.file import FileUpdate

MediaTypes = Literal["text/csv", "application/pdf"]
Extensions = Literal[".csv", ".pdf", ".xlsx"]


Actions = Literal["read", "update", "create", "delete"]
Resource = Literal["appointment", "case", "track"]


@dataclass
class FileController:
    user: User
    session: AsyncSession | None = None
    case: Case | None = None
    track: Track | None = None
    appointment: Appointment | None = None

    def __post_init__(self):
        assert self.case is not None or self.track is not None or self.appointment is not None, (
            "Either case, track or appointment must be provided"
        )

    def __validate_user_permission(self, action: Literal["read", "update", "create", "delete"]):
        """
        Raises a NoPermission exception if the user does not have the required permission
        """
        required_permissions: dict[Resource, dict[Actions, Permissions]] = {
            "appointment": {
                "read": "appointment:file:read",
                "update": "appointment:file:update",
                "create": "appointment:file:create",
                "delete": "appointment:file:delete",
            },
            "case": {
                "read": "case:file:read",
                "update": "case:file:update",
                "create": "case:file:create",
                "delete": "case:file:delete",
            },
            "track": {
                "read": "track:file:read",
                "update": "track:file:update",
                "create": "track:file:create",
                "delete": "track:file:delete",
            },
        }

        required_resource: Resource | None = None
        if self.track:
            required_resource = "track"
        elif self.case:
            required_resource = "case"
        elif self.appointment:
            required_resource = "appointment"

        assert required_resource
        required_permission = required_permissions[required_resource][action]
        if not self.user.has_permission(required_permission):
            raise NoPermission(username=self.user.name, required_permission=required_permission)

    @property
    def __base_query(self):
        """
        Returns a query that selects files from only the provided case or track.
        """
        query = select(File)
        if self.track:
            query = query.where(File.track_id == self.track.id)
        elif self.case:
            query = query.where(File.case_id == self.case.id)
        elif self.appointment:
            query = query.where(File.appointment_id == self.appointment.id)
        else:
            raise NotImplementedError
        return query

    @property
    def _session(self):
        assert self.session
        return self.session

    def __validate_file_authorization(self, file: File):
        """
        Raise an HTTP error when the file does not belong to the specified case or track.
        """
        if self.case:
            if file.case_id != self.case.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="File does not belong to specified case"
                )
        elif self.track:
            if file.track_id != self.track.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="File does not belong to specified track"
                )
        elif self.appointment:
            if file.appointment_id != self.appointment.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="File does not belong to specified appointment"
                )
        else:
            raise NotImplementedError

    def __validate_file_size(self, file: UploadFile):
        MAX_FILE_SIZE_MB = 50
        file.file.seek(0, 2)  # Move to end of file
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start

        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Bestand is te groot. Maximale grootte is {MAX_FILE_SIZE_MB} MB.",
            )

    async def get_files(self):
        self.__validate_user_permission("read")
        files = list((await self._session.scalars(self.__base_query)).unique())
        return files

    async def store_file(self, file: UploadFile, file_type: FileType, email_notifier: EmailNotifier):
        self.__validate_file_size(file)
        self.__validate_user_permission("create")
        malware_scan_results = scan_file_for_malware(file)
        if not malware_scan_results.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Het bestand bevat mogelijk schadelijke gegevens.",
            )

        # Check if file already exists
        existing_file = await self._session.scalar(self.__base_query.where(File.filename == file.filename))
        if existing_file:
            error_msg = f"Dit {'dossier' if self.case else 'track'} bevat al een bestand met de naam {file.filename}"
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=error_msg)

        file_content = file.file
        assert file.filename
        minio_object_id = minio_service.store_file(file_content)
        new_file = File(
            filename=file.filename, object_id=minio_object_id, file_type=file_type, uploaded_by_user=self.user
        )
        if self.track:
            new_file.track = self.track
        elif self.case:
            new_file.case = self.case
        elif self.appointment:
            new_file.appointment = self.appointment
        else:
            raise NotImplementedError
        self._session.add(new_file)

        self.send_notifications(
            subject="Bestand toegevoegd",
            message=f"{self.__get_file_description()} is toegevoegd.",
            email_notifier=email_notifier,
        )

    def download(self, file: File):
        """
        Downloads a file from MinIO.
        """
        self.__validate_file_authorization(file)
        self.__validate_user_permission("read")

        downloaded_file = minio_service.get_file(object_id=file.object_id)

        extension_media_type_mapping: dict[Extensions, MediaTypes] = {
            ".csv": "text/csv",
            ".pdf": "application/pdf",
        }

        extension = Path(file.filename).suffix.lower()
        if extension not in extension_media_type_mapping:
            raise HTTPException(status_code=400, detail="Unsupported file extension")

        media_type = extension_media_type_mapping[extension]

        return StreamingResponse(
            content=downloaded_file,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={file.filename}"},
        )

    def update_file_meta(self, file: File, file_update: FileUpdate, email_notifier: EmailNotifier):
        self.__validate_file_authorization(file)
        self.__validate_user_permission("update")
        has_approval_change = file.approved != file_update.approved
        if has_approval_change and not self.user.has_permission("file:approve"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to approve files.",
            )

        # First update the approval
        file.approved = file_update.approved
        if file_update.approved:
            file.approved_by_user = self.user
            file.approved_at = datetime.datetime.now(tz=datetime.timezone.utc) if file_update.approved else None

            self.send_notifications(
                subject="Bestand goedgekeurd",
                message=f"{self.__get_file_description()} is goedgekeurd.",
                email_notifier=email_notifier,
            )

        if not file_update.approved and file.approved:
            self.send_notifications(
                subject="Goedkeuring op bestand ingetrokken",
                message=f"{self.__get_file_description()} had goedkeuring. Deze goedkeuring is ingetrokken..",
                email_notifier=email_notifier,
            )

        # Update the remainder
        if file.description != file_update.description and has_approval_change:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Een goedgekeurd bestand kan niet gewijzigd worden.",
            )

        file.description = file_update.description

    def __get_file_description(self):
        if self.case:
            return "Een bestand in het dossier"
        elif self.track:
            return f"Een bestand in het traject {self.track.track_type_name}"
        elif self.appointment:
            return f"Een bestand in het gesprek {self.appointment.appointment_type.name}"
        else:
            raise NotImplementedError("Either case, track or appointment must be provided")

    @property
    def __relevant_case(self):
        if self.case:
            return self.case
        elif self.track:
            return self.track.case
        elif self.appointment:
            return self.appointment.case
        else:
            raise NotImplementedError("Either case, track or appointment must be provided")

    def send_notifications(self, subject: str, message: str, email_notifier: EmailNotifier):
        case = self.__relevant_case
        content = [message]

        if case:
            email_notifier.notify_client(
                client=case.client,
                content=content,
                subject=subject,
            )
        if case and case.advisor:
            email_notifier.notify_user(
                user=case.advisor,
                content=content,
                subject=subject,
            )

        if self.track and self.track.partner_organization:
            email_notifier.notify_partner_organization(
                partner_organization=self.track.partner_organization, content=[message], subject=subject
            )

        elif self.appointment and self.appointment.partner_organization:
            email_notifier.notify_partner_organization(
                partner_organization=self.appointment.partner_organization, content=[message], subject=subject
            )

    async def delete_file(self, file: File, email_notifier: EmailNotifier, user: User):
        self.__validate_file_authorization(file)
        self.__validate_user_permission("delete")
        self.send_notifications(
            subject="Bestand verwijderd",
            message=f"{self.__get_file_description()} is verwijderd.",
            email_notifier=email_notifier,
        )
        if self.case and file.case_id != user.active_case_id and user.has_role("ondernemer"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File does not belong to case of user with role {user.role}",
            )
        await self._session.delete(file)
