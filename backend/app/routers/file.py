from fastapi import APIRouter, Depends, UploadFile

import app.middleware.dependencies as deps
from app.controllers.file import FileController
from app.core.models import File, User
from app.core.types import FileType
from app.middleware.email_notification import EmailNotifier
from app.schemas.file import FileBase, FileUpdate

router = APIRouter(tags=["file"], prefix="/file")


@router.post("/")
async def upload_file(
    file: UploadFile,
    file_type: FileType,
    email_notifier: EmailNotifier = Depends(deps.get_email_notifier),
    file_controller: FileController = Depends(deps.get_file_controller),
):
    minio_object_id = await file_controller.store_file(file=file, file_type=file_type, email_notifier=email_notifier)
    return minio_object_id


@router.get("/", response_model=list[FileBase])
async def get_files(
    file_controller: FileController = Depends(deps.get_file_controller),
):
    return await file_controller.get_files()


@router.get("/{file_id}")
async def download_file(
    file: File = Depends(deps.get_file),
    file_controller: FileController = Depends(deps.get_file_controller),
):
    return file_controller.download(file=file)


@router.put("/{file_id}")
async def update_file(
    file_update: FileUpdate,
    email_notifier: EmailNotifier = Depends(deps.get_email_notifier),
    file_controller: FileController = Depends(deps.get_file_controller),
    file: File = Depends(deps.get_file),
):
    file_controller.update_file_meta(file, file_update, email_notifier=email_notifier)
    return


@router.delete("/{file_id}")
async def delete_file(
    file: File = Depends(deps.get_file),
    email_notifier: EmailNotifier = Depends(deps.get_email_notifier),
    file_controller: FileController = Depends(deps.get_file_controller),
    user: User = Depends(deps.get_logged_in_user),
):
    await file_controller.delete_file(file, email_notifier=email_notifier, user=user)
    pass
