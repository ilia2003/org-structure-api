from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import UUIDModel
from app.schemas.employees import EmployeeSchema
from app.schemas.mixins import CreateUpdateAt, StripTextFieldsMixin


class DepartmentSchema(UUIDModel, CreateUpdateAt, StripTextFieldsMixin):
    """
    Базовая схема получения подразделения (GET).
    """

    name: str = Field(..., max_length=200, examples=["Backend"])
    parent_id: UUID | None = Field(default=None)


class DepartmentCreateSchema(BaseModel, StripTextFieldsMixin):
    """
    Схема создания подразделения (POST).
    """

    name: str = Field(..., max_length=200, examples=["Backend"])
    parent_id: UUID | None = Field(default=None)


class DepartmentUpdateSchema(BaseModel, StripTextFieldsMixin):
    """
    Схема частичного обновления подразделения (PATCH).
    """

    name: str | None = Field(default=None, max_length=200, examples=["Backend"])
    parent_id: UUID | None = Field(default=None)


class DepartmentFullSchema(DepartmentSchema, StripTextFieldsMixin):
    """
    Расширенная схема подразделения с сотрудниками и дочерними подразделениями.
    """

    employees: list[EmployeeSchema] = Field(default_factory=list)
    children: list["DepartmentFullSchema"] = Field(default_factory=list)


DepartmentFullSchema.model_rebuild()
