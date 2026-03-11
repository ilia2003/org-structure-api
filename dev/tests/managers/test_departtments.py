import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.exceptions import BadRequestException, ConflictException, RequestedDataNotFoundException
from app.managers.departments import DepartmentManager
from app.schemas.departments import DepartmentCreateSchema, DepartmentSchema, DepartmentUpdateSchema
from dev.tests.factories import DepartmentFactory, EmployeeFactory


pytestmark = pytest.mark.asyncio


class TestDepartmentsSuccess:
    """✅ Success cases."""

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
        assert isinstance(expected_data, DepartmentSchema)
        session.commit.assert_awaited_once()

    @staticmethod
    async def test_create_department_with_parent(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        parent = DepartmentFactory(name="Head Office")
        department = DepartmentFactory(name="Platform", parent_id=parent.id)

        departments_db = SimpleNamespace(
            get_one=AsyncMock(side_effect=[parent, None]),
            create=AsyncMock(return_value=department),
        )
        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

        expected_data = await DepartmentManager.create_department(
            session=session,
            data=DepartmentCreateSchema(name="Platform", parent_id=parent.id),
        )

        assert expected_data.parent_id == parent.id
        assert expected_data.name == department.name
        session.commit.assert_awaited_once()

    @staticmethod
    async def test_update_department_name(monkeypatch) -> None:
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

    @staticmethod
    async def test_delete_department(monkeypatch) -> None:
        session = AsyncMock(spec=AsyncSession)
        source_department = DepartmentFactory(name="Legacy")
        target_department = DepartmentFactory(name="Core")
        employee = EmployeeFactory(department_id=source_department.id)

        departments_db = SimpleNamespace(
            get_one=AsyncMock(side_effect=[source_department, target_department]),
            delete=AsyncMock(),
        )
        employees_db = SimpleNamespace(
            get_all=AsyncMock(return_value=[employee]),
            update=AsyncMock(),
        )

        monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)
        monkeypatch.setattr("app.managers.departments.EmployeeCRUD", lambda _: employees_db)
        monkeypatch.setattr("app.managers.departments.check_target_not_in_subtree", AsyncMock())

        await DepartmentManager.delete_department(
            session=session,
            department_id=source_department.id,
            mode="reassign",
            reassign_to_department_id=target_department.id,
        )

        employees_db.update.assert_awaited_once_with(employee, department_id=target_department.id)
        departments_db.delete.assert_awaited_once_with(source_department)
        session.commit.assert_awaited_once()


class TestDepartmentsErrors:
    """❌ Error cases."""

    class TestNotFound:
        """404-like errors: RequestedDataNotFoundException"""

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
        async def test_create_department_parent_not_found(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            departments_db = SimpleNamespace(get_one=AsyncMock(return_value=None))
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

            with pytest.raises(RequestedDataNotFoundException, match="Parent department not found"):
                await DepartmentManager.create_department(
                    session=session,
                    data=DepartmentCreateSchema(name="Platform", parent_id=uuid.uuid4()),
                )

        @staticmethod
        async def test_update_department_not_found(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            departments_db = SimpleNamespace(get_one=AsyncMock(return_value=None))
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

            with pytest.raises(RequestedDataNotFoundException, match="Department not found"):
                await DepartmentManager.update_department(
                    session=session,
                    department_id=uuid.uuid4(),
                    data=DepartmentUpdateSchema(name="New name"),
                )

        @staticmethod
        async def test_delete_department_not_found(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            source_department = DepartmentFactory()

            departments_db = SimpleNamespace(
                get_one=AsyncMock(side_effect=[source_department, None]),
                delete=AsyncMock(),
            )
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)
            monkeypatch.setattr("app.managers.departments.EmployeeCRUD", lambda _: SimpleNamespace(get_all=AsyncMock()))

            with pytest.raises(RequestedDataNotFoundException, match="Target department not found"):
                await DepartmentManager.delete_department(
                    session=session,
                    department_id=source_department.id,
                    mode="reassign",
                    reassign_to_department_id=uuid.uuid4(),
                )

    class TestConflict:
        """409-like errors: ConflictException"""

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

        @staticmethod
        async def test_update_department_duplicate_name(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            department = DepartmentFactory(name="Platform")
            duplicate = DepartmentFactory(name="Platform Core")

            departments_db = SimpleNamespace(
                get_one=AsyncMock(side_effect=[department, duplicate]),
                update=AsyncMock(),
            )
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)

            with pytest.raises(ConflictException, match="Department with this name already exists"):
                await DepartmentManager.update_department(
                    session=session,
                    department_id=department.id,
                    data=DepartmentUpdateSchema(name=duplicate.name),
                )

        @staticmethod
        async def test_delete_department_reassign_to_same_department(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            source_department = DepartmentFactory()

            departments_db = SimpleNamespace(get_one=AsyncMock(return_value=source_department))
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)
            monkeypatch.setattr("app.managers.departments.EmployeeCRUD", lambda _: SimpleNamespace(get_all=AsyncMock()))

            with pytest.raises(ConflictException, match="Cannot reassign employees to the same department"):
                await DepartmentManager.delete_department(
                    session=session,
                    department_id=source_department.id,
                    mode="reassign",
                    reassign_to_department_id=source_department.id,
                )

    class TestBadRequest:
        """400-like errors: BadRequestException"""

        @staticmethod
        async def test_delete_department_unsupported_mode(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            source_department = DepartmentFactory()

            departments_db = SimpleNamespace(get_one=AsyncMock(return_value=source_department))
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)
            monkeypatch.setattr("app.managers.departments.EmployeeCRUD", lambda _: SimpleNamespace(get_all=AsyncMock()))

            with pytest.raises(BadRequestException, match="Unsupported delete mode"):
                await DepartmentManager.delete_department(
                    session=session,
                    department_id=source_department.id,
                    mode="hard-delete",
                )

        @staticmethod
        async def test_delete_department_reassign_without_target(monkeypatch) -> None:
            session = AsyncMock(spec=AsyncSession)
            source_department = DepartmentFactory()

            departments_db = SimpleNamespace(get_one=AsyncMock(return_value=source_department))
            monkeypatch.setattr("app.managers.departments.DepartmentCRUD", lambda _: departments_db)
            monkeypatch.setattr("app.managers.departments.EmployeeCRUD", lambda _: SimpleNamespace(get_all=AsyncMock()))

            with pytest.raises(BadRequestException, match="reassign_to_department_id is required"):
                await DepartmentManager.delete_department(
                    session=session,
                    department_id=source_department.id,
                    mode="reassign",
                    reassign_to_department_id=None,
                )
