from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.tenant import tenant_config
from app.core.types import RequiredProducts, TenantNames


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_DB: str = Field(default="postgres")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    LOG_LEVEL: Literal["DEBUG", "INFO"] = Field(min_length=1, default="INFO")
    APP_VERSION: str = Field(default="0.0.1", min_length=0)
    TENANT_NAME: TenantNames = Field(default="Gemeente Utrecht", min_length=1)

    # Generate a secret key with `head -c 24 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 32; echo`
    SECRET_KEY: str = Field(min_length=28, default="")
    CLIENT_BASE_URL: str = Field(default="", min_length=1)

    # Keycloak
    KEYCLOAK_URI: str = Field(default="https://s04.i8s.nl", min_length=1)
    KEYCLOAK_REALM: str = Field(default="oc_portaal", min_length=1)
    KEYCLOAK_CLIENT: str = Field(default="authentication-client", min_length=1)
    KEYCLOAK_API_CLIENT: str = Field(min_length=1, default="")
    KEYCLOAK_API_SECRET: str = Field(min_length=1, default="")
    KEYCLOAK_API_URI: str = Field(min_length=1, default="")
    KEYCLOAK_REQUIRE_EMAIL_VERIFICATION: Literal["0", "1"] = Field(default="1")
    DISABLE_AUTH: Literal["0", "1"] = Field(default="0")
    DEFAULT_ADMIN_USERNAME: str = Field(default="admin")
    REQUIRE_TOTP: Literal["0", "1"] = Field(default="0")

    # App config
    MOUNT_PATH: str = Field(default="/api")
    REQUIRED_PRODUCT_NAMES: set[RequiredProducts] = {"SHVO intake", "Toekomstgesprek"}

    # Email
    EMAIL_ENABLED: Literal["0", "1"] = Field(default="1")
    EMAIL_DOMAIN: str = Field(default="i8s.nl", min_length=1)
    EMAIL_CLIENT_NAME: str = Field(default="ictu-devops", min_length=1)
    EMAIL_RELAY_PASSWORD: str = Field(
        default="password",
        min_length=1,
        alias="EMAIL_RELAY_PASSWORD_I8S",
    )
    EMAIL_RELAY_HOSTNAME: str = Field(default="", min_length=0)
    EMAIL_ID_PREFIX: str = Field(default="OC", min_length=1)

    # Minio
    MINIO_HOST: str = Field(default="localhost", min_length=1)
    MINIO_HOST_PORT: int = Field(default=9000)
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", min_length=1)
    MINIO_SECRET_KEY: str = Field(default="minioadmin", min_length=1)
    MINIO_BUCKET_NAME: str = Field(default="oc-portaal", min_length=3)  # must be minimal 3 chars by Minio

    # ClamAV
    DISABLE_SECURITY_CHECK: Literal["0", "1"] = Field(default="0")
    CLAMAV_HOST: str = Field(min_length=0, default="")
    CLAMAV_PORT: int = Field(default=3310)

    # Development only
    OPENAI_API_KEY: str = Field(default="", min_length=0)

    @property
    def tenant_config(self):
        return tenant_config[self.TENANT_NAME]

    @model_validator(mode="after")
    def check_required_if_enabled(self):
        if self.EMAIL_ENABLED == "1":
            assert len(self.EMAIL_RELAY_HOSTNAME) > 0, "Variable EMAIL_RELAY_HOSTNAME is not set"
            assert len(self.EMAIL_DOMAIN) > 0, "Variable EMAIL_DOMAIN is not set"

        return self


settings = Settings()

assert settings.TENANT_NAME in tenant_config, f"Tenant '{settings.TENANT_NAME}' not found in tenant configuration"
