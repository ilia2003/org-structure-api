import importlib
import os
from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from dev.tests.factories import DepartmentFactory, EmployeeFactory


for key, value in {
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "postgres",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "postgres",
}.items():
    os.environ.setdefault(key, value)


@pytest.fixture
def seeded_db() -> dict[str, Any]:
    root_department = DepartmentFactory(name="Head Office")
    child_department = DepartmentFactory(name="Engineering", parent_id=root_department.id)
    second_department = DepartmentFactory(name="Finance", parent_id=root_department.id)

    employee_1 = EmployeeFactory(
        department_id=child_department.id,
        full_name="Alice Brown",
        position="Backend Engineer",
    )
    employee_2 = EmployeeFactory(
        department_id=child_department.id,
        full_name="Bob Green",
        position="QA Engineer",
    )

    return {
        "root_department": root_department,
        "child_department": child_department,
        "second_department": second_department,
        "departments": [root_department, child_department, second_department],
        "employees": [employee_1, employee_2],
    }


@pytest_asyncio.fixture
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    app = importlib.import_module("app.main").app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def missing_department_id() -> UUID:
    return uuid4()
