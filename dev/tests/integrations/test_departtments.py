import uuid
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.dependencies.exceptions import ConflictException, RequestedDataNotFoundException
from app.managers import Managers
from app.schemas.departments import DepartmentSchema, DepartmentTreeSchema
from app.schemas.employees import EmployeeSchema
from dev.tests.utils import assert_http_error


pytestmark = pytest.mark.asyncio


class TestDepartmentsApiSuccess:
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


class TestDepartmentsApiErrors:
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
    async def test_create_department_duplicate(api_client: AsyncClient, monkeypatch) -> None:
        monkeypatch.setattr(
            Managers.departments,
            "create_department",
            AsyncMock(side_effect=ConflictException("Department with this name already exists")),
        )

        resp = await api_client.post("/api/v1/departments", json={"name": "Engineering"})
        assert_http_error(resp, status.HTTP_409_CONFLICT, "Department with this name already exists")

    @staticmethod
    async def test_create_department_invalid_payload(api_client: AsyncClient) -> None:
        resp = await api_client.post("/api/v1/departments", json={})
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, resp.text
