from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import EmployeeCRUD
from dev.tests.factories import DepartmentFactory


pytestmark = pytest.mark.asyncio


class TestCrudSuccess:
    """✅ Success cases."""

    @staticmethod
    async def test_employee() -> None:
        session = AsyncMock(spec=AsyncSession)
        crud = EmployeeCRUD(session)

        await crud.create(
            department_id=DepartmentFactory().id,
            full_name="Alice Brown",
            position="QA",
            hired_at=None,
        )

        session.add.assert_called_once()
        session.flush.assert_awaited_once()
        session.refresh.assert_awaited_once()


class TestCrudErrors:
    """❌ Error cases."""

    @staticmethod
    async def test_get_all() -> None:
        session = AsyncMock(spec=AsyncSession)
        scalar_result = SimpleNamespace(all=MagicMock(return_value=[]))
        execute_result = SimpleNamespace(scalars=MagicMock(return_value=scalar_result))
        session.execute = AsyncMock(return_value=execute_result)

        actual = await EmployeeCRUD(session).get_all(department_id=DepartmentFactory().id)

        assert actual == []
