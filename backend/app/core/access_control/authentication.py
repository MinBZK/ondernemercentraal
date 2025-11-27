import logging
import time
from typing import Any, Dict

import jwt
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    ImmatureSignatureError,
    PyJWTError,
)
from pydantic import ValidationError

from app.core.exceptions import UserNotAuthenticated
from app.core.settings import settings
from keycloak import KeycloakOpenID  # type: ignore[reportAttributeAccessIssue]

logger = logging.getLogger(__name__)


class KeycloakAuth:
    def __init__(self):
        self.uri = settings.KEYCLOAK_API_URI
        self.realm = settings.KEYCLOAK_REALM
        self.client = settings.KEYCLOAK_REALM

        self.oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=f"{self.uri}/realms/{self.realm}/protocol/openid-connect/auth",
            tokenUrl=f"{self.uri}/realms/{self.realm}/protocol/openid-connect/token",
            auto_error=False,
        )
        self.cache: Dict[str, Any] = {}
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.uri,
            client_id=self.client,
            realm_name=self.realm,
        )

    def update_public_key(self, update_interval: int = 30) -> bool:
        current_time = time.time()
        if current_time - self.cache.get("keycloak_public_key_updated", 0) > update_interval:
            self.cache["keycloak_public_key"] = self.keycloak_openid.public_key()
            self.cache["keycloak_public_key_updated"] = current_time
            return True
        return False

    def get_public_key(self) -> str:
        if "keycloak_public_key" not in self.cache:
            logger.debug("Fetching public key")
            self.cache["keycloak_public_key"] = self.keycloak_openid.public_key()
            self.cache["keycloak_public_key_updated"] = time.time()
        return self.cache["keycloak_public_key"]

    def decode_token(self, token: str):
        logger.debug("Authorizing")
        public_key = self.get_public_key()
        keycloak_public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

        try:
            decoded_token = jwt.decode(
                token,
                key=keycloak_public_key,
                options={"verify_signature": True, "verify_aud": False, "exp": True},
                algorithms=["RS256"],
            )
            return decoded_token
        except ExpiredSignatureError:
            logger.warning("Session expired")
            raise UserNotAuthenticated("Session expired")
        except DecodeError:
            if self.update_public_key():
                logger.warning("Could not decode token. Updating public key and retrying once")
                return self.decode_token(token)
            logger.info("Could not decode token")
            raise UserNotAuthenticated("Could not decode token")
        except ImmatureSignatureError:
            logger.warning("Token not yet valid, retrying")
            time.sleep(0.5)
            return self.decode_token(token)
        except PyJWTError as e:
            logger.warning(f"JWT validation error: {str(e)}")
            raise UserNotAuthenticated("Invalid token")
        except Exception as e:
            logger.warning(f"Unexpected error during token decoding: {str(e)}")
            raise UserNotAuthenticated("Unexpected error during token decoding")

    @staticmethod
    def handle_validation_error(e: ValidationError) -> None:
        logger.debug(e)
        raise UserNotAuthenticated()


keycloak_auth = KeycloakAuth()
