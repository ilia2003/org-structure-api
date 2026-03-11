from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.exceptions import RequestedDataNotFoundException
from app.managers.employees import EmployeeManager
from app.schemas.employees import EmployeeCreateSchema, EmployeeSchema
from dev.tests.factories import DepartmentFactory, EmployeeFactory


pytestmark = pytest.mark.asyncio


class TestEmployeeManager:
    @staticmethod
    async def test_create_employee_success(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        department = DepartmentFactory()
        employee = EmployeeFactory(department_id=department.id)

        departments_db = SimpleNamespace(get_one=AsyncMock(return_value=department))
        employees_db = SimpleNamespace(create=AsyncMock(return_value=employee))

        monkeypatch.setattr("app.managers.employees.DepartmentCRUD", lambda _: departments_db)
        monkeypatch.setattr("app.managers.employees.EmployeeCRUD", lambda _: employees_db)

        data = EmployeeCreateSchema(
            full_name="Alice Brown",
            position="Backend Engineer",
            hired_at=None,
        )

        result = await EmployeeManager.create_employee(
            session=session,
            department_id=department.id,
            data=data,
        )

        assert isinstance(result, EmployeeSchema)
        assert result.department_id == department.id
        session.commit.assert_awaited_once()

    @staticmethod
    async def test_create_employee_department_not_found(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)

        departments_db = SimpleNamespace(get_one=AsyncMock(return_value=None))
        employees_db = SimpleNamespace(create=AsyncMock())

        monkeypatch.setattr("app.managers.employees.DepartmentCRUD", lambda _: departments_db)
        monkeypatch.setattr("app.managers.employees.EmployeeCRUD", lambda _: employees_db)

        with pytest.raises(RequestedDataNotFoundException, match="Department not found"):
            await EmployeeManager.create_employee(
                session=session,
                department_id=DepartmentFactory().id,
                data=EmployeeCreateSchema(full_name="Test", position="QA"),
            )

        employees_db.create.assert_not_called()
