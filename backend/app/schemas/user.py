from uuid import UUID

from pydantic import BaseModel, computed_field

from app.config.permissions import Permissions
from app.core.types import RoleNames

from .base import BaseSchema
from .role import Role


class UserUpdate(BaseModel):
    role_name: RoleNames
    partner_organization_name: str | None
    active: bool


class UserCreate(UserUpdate):
    name: str


class UserBase(BaseSchema, UserCreate):
    pass


class UserWithPermissions(UserCreate):
    permissions: list[Permissions]


class User(UserWithPermissions, UserBase):
    role: Role
    partner_organization_name: str | None


class UserWithCase(User):
    active_case_id: UUID | None


class UserPasswordUpdate(BaseModel):
    password: str


class UserCreated(UserPasswordUpdate):
    name: str
    password: str
    has_email: bool

    @property
    def __email(self):
        if self.has_email:
            return self.name

    @computed_field
    @property
    def message(self) -> list[str]:
        """
        A message that explains what has been done and what the next steps are.
        """
        messages = [
            f"Er is een account aangemaakt met gebruikersnaam '{self.name}' en een tijdelijk wachtwoord: {self.password}"  # noqa: E501
        ]
        if self.__email is not None:
            messages.append(f"Er is een e-mail verstuurd naar '{self.__email}' met deze informatie.")
        return messages
