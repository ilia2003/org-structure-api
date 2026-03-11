from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import DepartmentCRUD, EmployeeCRUD
from dev.tests.factories import DepartmentFactory


pytestmark = pytest.mark.asyncio


class TestCrudSuccess:
    """✅ Success cases."""

    @staticmethod
    async def test_department_crud_get_one() -> None:
        session = AsyncMock(spec=AsyncSession)
        department = DepartmentFactory(name="Engineering")

        execute_result = SimpleNamespace(scalar_one_or_none=MagicMock(return_value=department))
        session.execute = AsyncMock(return_value=execute_result)

        actual = await DepartmentCRUD(session).get_one(name=department.name)

        assert actual == department
        session.execute.assert_awaited_once()

    @staticmethod
    async def test_department_crud_get_all() -> None:
        session = AsyncMock(spec=AsyncSession)
        department_1 = DepartmentFactory(name="Engineering")
        department_2 = DepartmentFactory(name="Finance")

        scalar_result = SimpleNamespace(all=MagicMock(return_value=[department_1, department_2]))
        execute_result = SimpleNamespace(scalars=MagicMock(return_value=scalar_result))
        session.execute = AsyncMock(return_value=execute_result)

        actual = await DepartmentCRUD(session).get_all(parent_id=None)

        expected_count = 2
        assert len(actual) == expected_count
        assert actual[0].name == "Engineering"
        assert actual[1].name == "Finance"

    @staticmethod
    async def test_department_crud_update() -> None:
        session = AsyncMock(spec=AsyncSession)
        crud = DepartmentCRUD(session)
        department = DepartmentFactory(name="Old Name")

        actual = await crud.update(department, name="New Name")

        assert actual.name == "New Name"
        session.flush.assert_awaited_once()
        session.refresh.assert_awaited_once_with(department)

    @staticmethod
    async def test_department_crud_delete() -> None:
        session = AsyncMock(spec=AsyncSession)
        crud = DepartmentCRUD(session)
        department = DepartmentFactory()

        await crud.delete(department)

        session.delete.assert_awaited_once_with(department)
        session.flush.assert_awaited_once()


class TestCrudErrors:
    """❌ Error cases."""

    @staticmethod
    async def test_get_one() -> None:
        session = AsyncMock(spec=AsyncSession)
        execute_result = SimpleNamespace(scalar_one_or_none=MagicMock(return_value=None))
        session.execute = AsyncMock(return_value=execute_result)

        actual = await DepartmentCRUD(session).get_one(id=DepartmentFactory().id)

        assert actual is None


    @staticmethod
    async def test_create() -> None:
        session = AsyncMock(spec=AsyncSession)
        session.flush.side_effect = RuntimeError("flush failed")

        with pytest.raises(RuntimeError, match="flush failed"):
            await DepartmentCRUD(session).create(name="Engineering", parent_id=None)

    @staticmethod
    async def test_delete() -> None:
        session = AsyncMock(spec=AsyncSession)
        session.delete.side_effect = RuntimeError("delete failed")
        department = DepartmentFactory()

        with pytest.raises(RuntimeError, match="delete failed"):
            await DepartmentCRUD(session).delete(department)
