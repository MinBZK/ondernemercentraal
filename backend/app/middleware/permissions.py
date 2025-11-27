from fastapi import Depends

from app.config.permissions import Permissions
from app.core.models import User
from app.middleware.dependencies import get_logged_in_user
from app.util.logger import logger

from .exceptions import NoPermission


class PermissionChecker:
    def __init__(self, required_permission: Permissions):
        self.required_permission: Permissions = required_permission

    def __call__(self, user: User = Depends(get_logged_in_user)):
        if not user.has_permission(self.required_permission):
            logger.error(f"Gebruiker {user.name} heeft niet de juiste rechten: {self.required_permission}")
            raise NoPermission(username=user.name, required_permission=self.required_permission)
        return
