import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.dependencies.exceptions import RequestedDataNotFoundException
from app.managers import Managers
from app.schemas.employees import EmployeeSchema
from dev.tests.utils import assert_http_error


pytestmark = pytest.mark.asyncio


class TestEmployeesApi:
    @staticmethod
    async def test_create_employee_success(api_client: AsyncClient, seeded_db, monkeypatch) -> None:
        department = seeded_db["child_department"]
        employee = seeded_db["employees"][0]

        monkeypatch.setattr(
            Managers.employees,
            "create_employee",
            AsyncMock(return_value=EmployeeSchema.model_validate(employee)),
        )

        response = await api_client.post(
            f"/api/v1/departments/{department.id}/employees",
            json={"full_name": employee.full_name, "position": employee.position},
        )

        assert response.status_code == status.HTTP_201_CREATED, response.text
        payload = response.json()
        assert payload["department_id"] == str(department.id)
        assert payload["full_name"] == employee.full_name

    @staticmethod
    async def test_create_employee_not_found(api_client: AsyncClient, monkeypatch) -> None:
        monkeypatch.setattr(
            Managers.employees,
            "create_employee",
            AsyncMock(side_effect=RequestedDataNotFoundException("Department not found")),
        )

        response = await api_client.post(
            f"/api/v1/departments/{uuid.uuid4()}/employees",
            json={"full_name": "Alice", "position": "QA"},
        )

        assert_http_error(response, status.HTTP_404_NOT_FOUND, "Department not found")

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"full_name": "", "position": "QA"},
            {"full_name": "   ", "position": "QA"},
            {"full_name": "Alice", "position": ""},
            {"full_name": "Alice", "position": "   "},
            {"full_name": "x" * 201, "position": "QA"},
            {"full_name": "Alice", "position": "x" * 201},
        ],
    )
    async def test_create_employee_invalid_payload(
        api_client: AsyncClient,
        seeded_db,
        payload: dict,
    ) -> None:
        department = seeded_db["child_department"]
        response = await api_client.post(f"/api/v1/departments/{department.id}/employees", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT, response.text
