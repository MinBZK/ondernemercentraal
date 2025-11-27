import datetime
import uuid
from dataclasses import dataclass
from typing import Literal

import jwt
from pydantic import BaseModel, Field, computed_field

from app.core.settings import settings

TokenType = Literal["initial", "email_confirmation"]


class TokenPayload(BaseModel):
    client_id: str
    exp: datetime.datetime
    iat: datetime.datetime


@dataclass
class ConfirmationTokenHandler:
    algorithm: str = "HS256"
    token_expiry_seconds: int = 60 * 60

    def create_token(self, client_id: uuid.UUID):
        payload = TokenPayload(
            client_id=str(client_id),
            exp=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=self.token_expiry_seconds),
            iat=datetime.datetime.now(datetime.timezone.utc),
        )
        return jwt.encode(payload.model_dump(), settings.SECRET_KEY, algorithm=self.algorithm)

    def parse_token(self, token: str):
        return TokenPayload.model_validate(jwt.decode(token, settings.SECRET_KEY, algorithms=[self.algorithm]))


class TokenValidationResponse(BaseModel):
    token: str = Field(exclude=True)

    @computed_field
    @property
    def decoded_token(self) -> TokenPayload:
        return ConfirmationTokenHandler().parse_token(self.token)
