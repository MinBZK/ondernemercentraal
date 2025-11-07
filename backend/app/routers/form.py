from typing import Literal

from fastapi import APIRouter, Depends

import app.core.models as models
import app.middleware.dependencies as deps
from app.controllers.form import FormController, update_form_status
from app.core.models.payload_validation import PayloadValidation
from app.core.types import FormStatus
from app.middleware.email_notification import EmailNotifier
from app.middleware.permissions import PermissionChecker
from app.schemas.form_data import FormData, FormDataUpsert
from app.schemas.form_template import FormTemplate

router = APIRouter(tags=["form"])

FormResourceNames = Literal["appointment"]


@router.post("/form-template/{form_name}/validation", response_model=PayloadValidation)
async def validate_form_template(
    payload: dict,
    form_template: models.FormTemplate = Depends(deps.get_form_template),
):
    validation_errors = form_template.get_payload_validation(payload)
    return validation_errors


@router.get(
    "/form-template/{form_name}", response_model=FormTemplate, dependencies=[Depends(PermissionChecker("form:read"))]
)
async def get_form_template(
    form_template: models.FormTemplate = Depends(deps.get_form_template),
):
    return form_template


@router.get("/form-data", dependencies=[Depends(PermissionChecker("form:read"))], response_model=list[FormData])
async def get_forms(
    form_controller: FormController = Depends(deps.get_form_controller),
):
    return await form_controller.get_forms()


@router.get(
    "/form-data/{form_data_id}", dependencies=[Depends(PermissionChecker("form:read"))], response_model=FormData
)
async def get_one_form(
    form_data: models.FormData = Depends(deps.get_form_data),
):
    return form_data


@router.post("/form-data/", dependencies=[Depends(PermissionChecker("form:create"))], response_model=FormData)
async def create_form_data(
    form_data_upsert: FormDataUpsert,
    form_template: models.FormTemplate = Depends(get_form_template),
    form_controller: FormController = Depends(deps.get_form_controller),
    user: models.User = Depends(deps.get_logged_in_user),
):
    form_data = await form_controller.create_form_data(form_template=form_template)
    await form_controller.upsert_form_data(form_data_upsert=form_data_upsert, user=user, form_data=form_data)
    return form_data


@router.put("/form-data/{form_data_id}", dependencies=[Depends(PermissionChecker("form:update"))])
async def update_form_data(
    form_data_upsert: FormDataUpsert,
    form_controller: FormController = Depends(deps.get_form_controller),
    form_data: models.FormData = Depends(deps.get_form_data),
    user: models.User = Depends(deps.get_logged_in_user),
):
    await form_controller.upsert_form_data(form_data_upsert=form_data_upsert, user=user, form_data=form_data)
    return


@router.put("/form-data/{form_data_id}/status/{form_status}")
async def update_form_data_status(
    form_status: FormStatus,
    form_data: models.FormData = Depends(deps.get_form_data),
    user: models.User = Depends(deps.get_logged_in_user),
    email_notifier: EmailNotifier = Depends(deps.get_email_notifier),
):
    await update_form_status(form_data=form_data, user=user, target_status=form_status, email_notifier=email_notifier)
    return
