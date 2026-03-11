from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.departments import DepartmentCRUD
from app.db.crud.employees import EmployeeCRUD
from app.dependencies.exceptions import RequestedDataNotFoundException
from app.schemas.employees import EmployeeCreateSchema, EmployeeSchema


class EmployeeManager:
    """Business logic for employees."""

    @staticmethod
    async def create_employee(
        session: AsyncSession,
        department_id: UUID,
        data: EmployeeCreateSchema,
    ) -> EmployeeSchema:
        departments_db = DepartmentCRUD(session)
        employees_db = EmployeeCRUD(session)

        department = await departments_db.get_one(id=department_id)
        if not department:
            raise RequestedDataNotFoundException("Department not found")

        employee = await employees_db.create(
            department_id=department_id,
            **data.model_dump(),
        )
        await session.commit()
        return EmployeeSchema.model_validate(employee)
