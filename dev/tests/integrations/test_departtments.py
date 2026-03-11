import uuid
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.dependencies.exceptions import BadRequestException, ConflictException, RequestedDataNotFoundException
from app.managers import Managers
from app.schemas.departments import DepartmentSchema, DepartmentTreeSchema
from app.schemas.employees import EmployeeSchema
from dev.tests.utils import assert_http_error


pytestmark = pytest.mark.asyncio


class TestDepartmentsApiSuccess:
    """✅ Success cases."""

    @staticmethod
    async def test_create_department(api_client: AsyncClient, seeded_db: dict[str, Any], monkeypatch) -> None:
        department = seeded_db["child_department"]
        manager_result = DepartmentSchema.model_validate(department)
        monkeypatch.setattr(Managers.departments, "create_department", AsyncMock(return_value=manager_result))

        resp = await api_client.post("/api/v1/departments", json={"name": department.name})
        assert resp.status_code == status.HTTP_201_CREATED, resp.text

        data = resp.json()
        assert data["id"] == str(department.id)
        assert data["name"] == department.name

    @staticmethod
    async def test_get_department_tree(api_client: AsyncClient, seeded_db: dict[str, Any], monkeypatch) -> None:
        root = seeded_db["root_department"]
        child = seeded_db["child_department"]
        expected_employee_count = len(seeded_db["employees"])
        employees = [EmployeeSchema.model_validate(item) for item in seeded_db["employees"]]

        tree = DepartmentTreeSchema(
            department=DepartmentSchema.model_validate(root),
            employees=[],
            children=[
                DepartmentTreeSchema(
                    department=DepartmentSchema.model_validate(child),
                    employees=employees,
                    children=[],
                )
            ],
        )

        monkeypatch.setattr(Managers.departments, "get_department", AsyncMock(return_value=tree))

        resp = await api_client.get(f"/api/v1/departments/{root.id}?depth=2&include_employees=true")
        assert resp.status_code == status.HTTP_200_OK, resp.text

        data = resp.json()
        assert data["department"]["id"] == str(root.id)
        assert len(data["children"]) == 1
        assert data["children"][0]["department"]["id"] == str(child.id)
        assert len(data["children"][0]["employees"]) == expected_employee_count

    @staticmethod
    async def test_delete_department_no_content(
        api_client: AsyncClient, seeded_db: dict[str, Any], monkeypatch
    ) -> None:
        department = seeded_db["child_department"]
        monkeypatch.setattr(Managers.departments, "delete_department", AsyncMock(return_value=None))

        resp = await api_client.delete(f"/api/v1/departments/{department.id}?mode=cascade")

        assert resp.status_code == status.HTTP_204_NO_CONTENT, resp.text
        assert resp.text == ""


class TestDepartmentsApiErrors:
    """❌ Error cases."""

    class TestNotFound:
        """404-like errors: RequestedDataNotFoundException"""

        @staticmethod
        async def test_get_department_not_found(api_client: AsyncClient, monkeypatch) -> None:
            monkeypatch.setattr(
                Managers.departments,
                "get_department",
                AsyncMock(side_effect=RequestedDataNotFoundException("Department not found")),
            )

            resp = await api_client.get(f"/api/v1/departments/{uuid.uuid4()}")
            assert_http_error(resp, status.HTTP_404_NOT_FOUND, "Department not found")

        @staticmethod
        async def test_delete_department_target_not_found(
            api_client: AsyncClient, seeded_db: dict[str, Any], monkeypatch
        ) -> None:
            department = seeded_db["child_department"]
            monkeypatch.setattr(
                Managers.departments,
                "delete_department",
                AsyncMock(side_effect=RequestedDataNotFoundException("Target department not found")),
            )

            resp = await api_client.delete(
                f"/api/v1/departments/{department.id}?mode=reassign&reassign_to_department_id={uuid.uuid4()}"
            )
            assert_http_error(resp, status.HTTP_404_NOT_FOUND, "Target department not found")

    class TestConflict:
        """409-like errors: ConflictException"""

        @staticmethod
        async def test_create_department_duplicate(api_client: AsyncClient, monkeypatch) -> None:
            monkeypatch.setattr(
                Managers.departments,
                "create_department",
                AsyncMock(side_effect=ConflictException("Department with this name already exists")),
            )

            resp = await api_client.post("/api/v1/departments", json={"name": "Engineering"})
            assert_http_error(resp, status.HTTP_409_CONFLICT, "Department with this name already exists")

        @staticmethod
        async def test_update_department_conflict(
            api_client: AsyncClient, seeded_db: dict[str, Any], monkeypatch
        ) -> None:
            department = seeded_db["child_department"]
            monkeypatch.setattr(
                Managers.departments,
                "update_department",
                AsyncMock(side_effect=ConflictException("Department cannot be parent of itself")),
            )

            resp = await api_client.patch(
                f"/api/v1/departments/{department.id}",
                json={"parent_id": str(department.id)},
            )
            assert_http_error(resp, status.HTTP_409_CONFLICT, "Department cannot be parent of itself")

    class TestBadRequest:
        """400-like errors: BadRequestException"""

        @staticmethod
        async def test_delete_department_bad_mode(
            api_client: AsyncClient, seeded_db: dict[str, Any], monkeypatch
        ) -> None:
            department = seeded_db["child_department"]
            monkeypatch.setattr(
                Managers.departments,
                "delete_department",
                AsyncMock(side_effect=BadRequestException("Unsupported delete mode")),
            )

            resp = await api_client.delete(f"/api/v1/departments/{department.id}?mode=cascade")
            assert_http_error(resp, status.HTTP_400_BAD_REQUEST, "Unsupported delete mode")

    class TestValidation:
        """🧪 Validation errors."""

        @staticmethod
        @pytest.mark.parametrize(
            "payload",
            [
                {},
                {"name": 123},
                {"name": "x" * 201},
            ],
        )
        async def test_create_department_invalid_payload(
            api_client: AsyncClient,
            payload: dict[str, Any],
        ) -> None:
            resp = await api_client.post("/api/v1/departments", json=payload)
            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, resp.text

        @staticmethod
        @pytest.mark.parametrize(
            "payload",
            [
                {"name": "x" * 201},
                {"parent_id": "not-uuid"},
            ],
        )
        async def test_update_department_invalid_payload(
            api_client: AsyncClient,
            seeded_db: dict[str, Any],
            payload: dict[str, Any],
        ) -> None:
            department = seeded_db["child_department"]

            resp = await api_client.patch(f"/api/v1/departments/{department.id}", json=payload)
            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, resp.text

        @staticmethod
        async def test_delete_department_invalid_mode_pattern(
            api_client: AsyncClient,
            seeded_db: dict[str, Any],
        ) -> None:
            department = seeded_db["child_department"]
            resp = await api_client.delete(f"/api/v1/departments/{department.id}?mode=hard-delete")
            assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, resp.text
