from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.postgresql import get_session


SessionDepends = Annotated[AsyncSession, Depends(get_session)]

class RequestedDataNotFoundException(HTTPException):
    """404 — данные не найдены"""

    def __init__(self, detail: str = "Requested data not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(HTTPException):
    """409 — конфликт данных"""

    def __init__(self, detail: str = "Conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class BadRequestException(HTTPException):
    """400 — неправильный запрос"""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class PermissionDeniedException(HTTPException):
    """403 — нет прав"""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
