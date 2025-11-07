from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import app.middleware.dependencies as deps
import app.schemas.request as schemas
from app.controllers.request import upsert_request
from app.core.models import Case, Request, User
from app.core.models.request import RequestName
from app.core.types import FormNames
from app.middleware.dependencies import get_case, get_request
from app.middleware.permissions import PermissionChecker
from app.schemas.form_data import FormDataUpsert

router = APIRouter(prefix="", tags=["Request"])


@router.post("/case/{case_id}/request", dependencies=[Depends(PermissionChecker("request:create"))])
async def create_request(
    request_create: schemas.RequestUpsert,
    case: Case = Depends(get_case),
    user: User = Depends(deps.get_logged_in_user),
    session: AsyncSession = Depends(deps.get_db_session),
):
    new_request = Request()
    await upsert_request(new_request, request_create, case)

    form_template_mapping: dict[RequestName, FormNames] = {
        "IOAZ-aanvraag": "IOAZ-aanvraag",
        "BBZ-aanvraag": "BBZ-aanvraag",
        "BBZ-verlenging-aanvraag": "BBZ-verlenging-aanvraag",
    }
    form_name = form_template_mapping[new_request.name]
    form_template = await deps.get_form_template(form_name=form_name, session=session)
    form_controller = await deps.get_form_controller(
        session=session, request=new_request, user=user, track=None, appointment=None
    )
    # Refresh to get a request id
    session.add(new_request)
    await session.flush()
    await session.refresh(new_request)

    form_data = await form_controller.create_form_data(form_template)
    await form_controller.upsert_form_data(
        form_data=form_data, form_data_upsert=FormDataUpsert(payload=None), user=user
    )

    return


@router.put("/case/{case_id}/request/{request_id}", dependencies=[Depends(PermissionChecker("request:update"))])
async def update_request(
    request_create: schemas.RequestUpsert,
    case: Case = Depends(get_case),
    request: Request = Depends(get_request),
):
    if request.case_id != case.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Request does not belong to the specified case"
        )
    await upsert_request(request, request_create, case)
    return


@router.get(
    "/case/{case_id}/request/",
    dependencies=[Depends(PermissionChecker("request:read"))],
    response_model=list[schemas.Request],
)
async def get_requests(
    case: Case = Depends(get_case),
    session: AsyncSession = Depends(deps.get_db_session),
):
    requests = await session.scalars(
        select(Request).where(Request.case_id == case.id).options(joinedload(Request.case))
    )
    return list(requests.unique())


@router.delete("/case/{case_id}/request/{request_id}", dependencies=[Depends(PermissionChecker("request:delete"))])
async def delete_request(
    case: Case = Depends(get_case),
    request: Request = Depends(get_request),
    session: AsyncSession = Depends(deps.get_db_session),
):
    if request.case_id != case.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Request does not belong to the specified case"
        )
    await session.delete(request)
    return
