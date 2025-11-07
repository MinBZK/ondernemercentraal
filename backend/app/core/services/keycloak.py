import json
import secrets
from dataclasses import dataclass
from uuid import UUID

from pydantic import BaseModel

from app.core.exceptions import InvalidInput
from app.core.settings import settings
from app.util.logger import get_logger
from keycloak import (
    KeycloakAdmin,
    KeycloakConnectionError,
    KeycloakDeleteError,
)

logger = get_logger(__name__)


@dataclass
class KeycloakUserCredentials:
    keycloak_user_id: str
    password: str


class KeycloakUser(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    emailVerified: bool
    createdTimestamp: int
    enabled: bool
    totp: bool
    requiredActions: list[str]


class KeycloakSyncError(Exception):
    pass


class KeycloakService:
    def __init__(self):
        self.__client: KeycloakAdmin | None = None

    def __get_keycloak_client(self):
        try:
            self.__client = KeycloakAdmin(
                server_url=settings.KEYCLOAK_API_URI,
                realm_name=settings.KEYCLOAK_REALM,
                client_id=settings.KEYCLOAK_API_CLIENT,
                client_secret_key=settings.KEYCLOAK_API_SECRET,
            )
            return self.__client
        except KeycloakConnectionError as e:
            logger.error(str(e))
            raise KeycloakSyncError("Geen verbinding met Keycloak mogelijk")

    def __generate_password(self):
        return secrets.token_urlsafe(16)

    @property
    def client(self):
        client = None
        if self.__client is None:
            client = self.__get_keycloak_client()
            self.__client = client
        else:
            client = self.__client

        return client

    @client.setter
    def set_client(self, client: KeycloakAdmin):
        self.__client = client

    def set_password(
        self,
        username: str,
        password_is_temporary: bool,
        password_override: str | None = None,
    ):
        password = self.__generate_password() if password_override is None else password_override
        user_id = self.client.get_user_id(username)
        assert user_id, f"User {username} does not exist and must be created first."
        self.client.update_user(
            user_id=user_id,
            payload={
                "credentials": [
                    {
                        "type": "password",
                        "temporary": password_is_temporary,
                        "value": password,
                    }
                ],
            },
        )
        return password

    def update_username(self, current_username: str, target_username: str):
        """
        Returns a tuple with keycloak user id and a password
        """
        existing_user_id = self.client.get_user_id(username=current_username)
        assert existing_user_id, f"User {current_username} does not exist."
        self.client.delete_user(existing_user_id)
        return self.create_user(target_username, password_is_temporary=True)

    def upsert_user(self, username: str, password_override: str | None = None):
        """
        Returns the Keycloak credentials for the upserted user
        """
        existing_user = self.get_user(username)
        if existing_user:
            password = self.set_password(username, password_override=password_override, password_is_temporary=True)
            return KeycloakUserCredentials(keycloak_user_id=str(existing_user.id), password=password)
        else:
            return self.create_user(
                username=username, password_override=password_override, password_is_temporary=password_override is None
            )

    def create_user(
        self,
        username: str,
        password_is_temporary: bool,
        password_override: str | None = None,
    ):
        """
        Returns a tuple with keycloak user id and a password
        """
        existing_user_id = self.client.get_user_id(username=username)
        if existing_user_id:
            raise InvalidInput(f"Gebruiker met gebruikersnaam {username} bestaat al.")

        password = self.__generate_password() if password_override is None else password_override
        required_actions = (
            [
                "UPDATE_PASSWORD",
            ]
            if password_override is None
            else []
        )
        if settings.REQUIRE_TOTP == "1":
            required_actions.append("CONFIGURE_TOTP")

        if settings.KEYCLOAK_REQUIRE_EMAIL_VERIFICATION == "1":
            required_actions.append("VERIFY_EMAIL")

        email = username if "@" in username else None

        user_id = self.client.create_user(
            {
                "username": username,
                "email": email,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "temporary": password_is_temporary,
                        "value": password,
                    }
                ],
                "requiredActions": required_actions,
            }
        )
        return KeycloakUserCredentials(keycloak_user_id=user_id, password=password)

    def delete_user(self, username: str):
        user_id = self.client.get_user_id(username)
        assert user_id
        try:
            return self.client.delete_user(user_id)
        except KeycloakDeleteError as e:
            logger.error(str(e))
            if e.response_body:
                error = json.loads(e.response_body).get("error")
                if error == "User not found":
                    return
            raise KeycloakSyncError(f"Gebruik {username} kan niet worden verwijderd in Keycloak")

    def get_user(self, username: str):
        user_id = self.client.get_user_id(username)
        if user_id:
            return KeycloakUser.model_validate(self.client.get_user(user_id))


keycloak_service = KeycloakService()
