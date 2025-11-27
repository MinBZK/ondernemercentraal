from fastapi import HTTPException, status

from app.config.permissions import Permissions
from app.util.logger import logger


class NoPermission(HTTPException):
    def __init__(self, username: str, required_permission: Permissions):
        logger.error(
            f"User {username} does not have the required permission: {required_permission}",
        )
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Je hebt niet de benodigde rechten om deze actie uit te voeren.",
        )
