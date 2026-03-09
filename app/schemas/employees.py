from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import UUIDModel
from app.schemas.mixins import CreateUpdateAt, StripTextFieldsMixin


class EmployeeSchema(UUIDModel, CreateUpdateAt, StripTextFieldsMixin):
    """
    Базовая схема получения сотрудника(GET).
    """

    department_id: UUID
    full_name: str = Field(..., max_length=200, examples=["John Smith"])
    position: str = Field(..., max_length=200, examples=["Backend Developer"])
    hired_at: date | None = None


class EmployeeCreateSchema(BaseModel, StripTextFieldsMixin):
    """
    Схема создания сотрудника(POST).
    """

    full_name: str = Field(..., max_length=200, examples=["John Smith"])
    position: str = Field(..., max_length=200, examples=["Backend Developer"])
    hired_at: date | None = None
