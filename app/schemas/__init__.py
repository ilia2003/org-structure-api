from app.schemas.base import BaseModel

from .departments import (
    DepartmentCreateSchema,
    DepartmentSchema,
    DepartmentTreeSchema,
    DepartmentUpdateSchema,
)
from .employees import EmployeeCreateSchema, EmployeeSchema


__all__ = [
    "DepartmentSchema",
    "DepartmentCreateSchema",
    "DepartmentUpdateSchema",
    "DepartmentTreeSchema",
    "EmployeeSchema",
    "EmployeeCreateSchema",
    "BaseModel"
]
