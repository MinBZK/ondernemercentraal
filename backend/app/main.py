from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.database import async_session
from app.core.services import minio_service
from app.core.settings import settings
from app.middleware.dependencies import get_logged_in_user
from app.routers import (
    appointment,
    appointment_public,
    appointment_slot,
    availability,
    case,
    client,
    client_public,
    comment,
    config,
    file,
    form,
    json_schema_validation,
    partner_organization,
    product,
    product_category,
    request,
    role,
    task,
    track,
    track_value,
    user,
    user_basic,
)
from app.schemas.user import UserWithCase
from app.scripts.validate_config import validate_products
from app.util.logger import logger

api_router = APIRouter(prefix=settings.MOUNT_PATH)

api_router.include_router(
    client_public.router,
)

api_router.include_router(availability.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(client.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(case.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(user.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(user_basic.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(role.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(file.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(track_value.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(track.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(appointment_slot.router)
api_router.include_router(appointment_public.router)
api_router.include_router(config.router)
api_router.include_router(appointment.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(task.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(form.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(product_category.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(product.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(partner_organization.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(request.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(json_schema_validation.router, dependencies=[Depends(get_logged_in_user)])
api_router.include_router(comment.router, dependencies=[Depends(get_logged_in_user)])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate Minio is working
    minio_service.check_initialization()
    async with async_session.begin() as session:
        await validate_products(session)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    logger.error(str(exc))
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return PlainTextResponse("Ongeldige invoer", status_code=422)


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.get("/me", response_model=UserWithCase)
async def get_me(
    user: str = Depends(get_logged_in_user),
):
    return user


app.include_router(api_router)
