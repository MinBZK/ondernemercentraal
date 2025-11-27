from typing import Optional

from fastapi import HTTPException, status


class HTTPInvalidInput(HTTPException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


class HTTPNotFound(HTTPException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )


class HTTPConflict(HTTPException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )


class UserNotAuthenticated(HTTPException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message or "Inloggegevens konden niet worden gevalideerd.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFound(HTTPException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message or "User not found",
        )


class UserNotAuthorized(HTTPException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message or "U bent niet bevoegd om deze actie uit te voeren.",
        )


class InvalidInput(Exception):
    def __init__(self, message: str | None = None):
        default_message = "Ongeldige invoer"
        message = message if message is not None else default_message
        super().__init__(message)
