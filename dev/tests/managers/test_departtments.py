import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.exceptions import ConflictException, RequestedDataNotFoundException
from app.managers.departments import DepartmentManager
from app.schemas.departments import DepartmentCreateSchema, DepartmentSchema, DepartmentUpdateSchema
from dev.tests.factories import DepartmentFactory


pytestmark = pytest.mark.asyncio


class TestDepartmentsSuccess:
    @staticmethod
    async def test_create_department(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        department = DepartmentFactory(name="Platform")

        departments_db = SimpleNamespace(
            get_one=AsyncMock(side_effect=[None]),
            create=AsyncMock(return_value=department),
        )
        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

        data = DepartmentCreateSchema(name="Platform")
        expected_data: DepartmentSchema = await DepartmentManager.create_department(session=session, data=data)

        assert expected_data.name == data.name
        assert expected_data.parent_id is None
        session.commit.assert_awaited_once()

    @staticmethod
    async def test_update_department(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        department = DepartmentFactory(name="Platform")
        updated_department = DepartmentFactory(
            id=department.id,
            name="Platform Core",
            parent_id=department.parent_id,
        )

        departments_db = SimpleNamespace(
            get_one=AsyncMock(side_effect=[department, None]),
            update=AsyncMock(return_value=updated_department),
        )
        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

        data = DepartmentUpdateSchema(name="Platform Core")
        expected_data = await DepartmentManager.update_department(
            session=session,
            department_id=department.id,
            data=data,
        )

        assert expected_data.name == data.name
        assert expected_data.id == department.id
        session.commit.assert_awaited_once()


class TestDepartmentsErrors:
    @staticmethod
    async def test_get_department_not_found(monkeypatch, missing_department_id: uuid.UUID) -> None:
        session = AsyncMock(spec=AsyncSession)
        departments_db = SimpleNamespace(get_one=AsyncMock(return_value=None))
        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

        with pytest.raises(RequestedDataNotFoundException, match="Department not found"):
            await DepartmentManager.get_department(
                session=session,
                department_id=missing_department_id,
                depth=1,
                include_employees=True,
            )

    @staticmethod
    async def test_create_department_duplicate_name(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        duplicate = DepartmentFactory(name="Platform")
        departments_db = SimpleNamespace(
            get_one=AsyncMock(return_value=duplicate),
            create=AsyncMock(),
        )
        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

        with pytest.raises(ConflictException, match="Department with this name already exists"):
            await DepartmentManager.create_department(
                session=session,
                data=DepartmentCreateSchema(name="Platform"),
            )

    @staticmethod
    async def test_update_department_to_self_parent(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        department = DepartmentFactory()
        departments_db = SimpleNamespace(get_one=AsyncMock(return_value=department))
        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

        with pytest.raises(ConflictException, match="Department cannot be parent of itself"):
            await DepartmentManager.update_department(
                session=session,
                department_id=department.id,
                data=DepartmentUpdateSchema(parent_id=department.id),
            )
