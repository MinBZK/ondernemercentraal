from fastapi import APIRouter
from pydantic import BaseModel

from app.config.tenant import TenantConfig
from app.core.settings import settings
from app.core.types import RequiredProducts

router = APIRouter(tags=["config"], prefix="/config")


class AppConfig(BaseModel):
    keycloak_uri: str
    keycloak_realm: str
    keycloak_client_id: str
    app_version: str
    tenant_name: str
    tenant_config: TenantConfig
    # By explicitly defining this in the config, the types are available in the frontend. We only need the types.
    required_products: list[RequiredProducts]


app_config = AppConfig(
    keycloak_uri=settings.KEYCLOAK_URI,
    keycloak_realm=settings.KEYCLOAK_REALM,
    keycloak_client_id=settings.KEYCLOAK_CLIENT,
    app_version=settings.APP_VERSION,
    tenant_name=settings.TENANT_NAME,
    tenant_config=settings.tenant_config,
    required_products=settings.REQUIRED_PRODUCT_NAMES,  # type: ignore
)


@router.get("/", response_model=AppConfig)
async def get_app_config():
    return app_config
