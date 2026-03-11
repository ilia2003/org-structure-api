from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.dependencies import SessionDepends
from app.managers import Managers
from app.schemas.departments import (
    DepartmentCreateSchema,
    DepartmentSchema,
    DepartmentTreeSchema,
    DepartmentUpdateSchema,
)
from app.schemas.employees import EmployeeCreateSchema, EmployeeSchema


router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DepartmentSchema,
)
async def create_department(
    data: DepartmentCreateSchema,
    session: SessionDepends,
) -> DepartmentSchema:
    """
    Create a new department.

    ### Input
    - **name** [max 200 chars]
    - **parent_id**: parent department UUID or null

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: department UUID
    - **name**: department name
    - **parent_id**: parent department UUID or null
    """
    return await Managers.departments.create_department(session=session, data=data)


@router.post(
    "/{department_id}/employees",
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeSchema,
)
async def create_employee(
    department_id: UUID,
    data: EmployeeCreateSchema,
    session: SessionDepends,
) -> EmployeeSchema:
    """
    Create a new employee in the selected department.

    ### Input
    - **department_id** (path): department UUID
    - **full_name** [max 200 chars]
    - **position** [max 200 chars]
    - **hired_at**: employee hiring date or null

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: employee UUID
    - **department_id**: department UUID
    - **full_name**: employee full name
    - **position**: employee position
    - **hired_at**: employee hiring date or null
    """
    return await Managers.employees.create_employee(
        session=session,
        department_id=department_id,
        data=data,
    )


@router.get(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentTreeSchema,
)
async def get_department(
    department_id: UUID,
    depth: int = Query(default=1, ge=1, le=5),
    include_employees: bool = Query(default=True),
    session: SessionDepends = None,
) -> DepartmentTreeSchema:
    """
    Retrieve a department with employees and nested child departments.

    ### Input
    - **department_id** (path): department UUID
    - **depth** (query): nested children depth, default 1, max 5
    - **include_employees** (query): include employees list or not

    ### Output
    - **department**: department object
    - **employees**: department employees list
    - **children**: nested child departments tree
    """
    return await Managers.departments.get_department(
        session=session,
        department_id=department_id,
        depth=depth,
        include_employees=include_employees,
    )


@router.patch(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentSchema,
)
async def update_department(
    department_id: UUID,
    data: DepartmentUpdateSchema,
    session: SessionDepends,
) -> DepartmentSchema:
    """
    Partially update a department.

    ### Input
    - **department_id** (path): department UUID
    - **name** [max 200 chars]
    - **parent_id**: parent department UUID or null

    ### Output
    - **created_at**: creation datetime
    - **updated_at**: last update datetime
    - **id**: department UUID
    - **name**: department name
    - **parent_id**: parent department UUID or null
    """
    return await Managers.departments.update_department(
        session=session,
        department_id=department_id,
        data=data,
    )


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
    department_id: UUID,
    mode: str = Query(..., pattern="(cascade|reassign)"),
    reassign_to_department_id: UUID | None = Query(default=None),
    session: SessionDepends = None,
) -> Response:
    """
    Delete a department.

    ### Input
    - **department_id** (path): department UUID
    - **mode** (query): delete mode, either `cascade` or `reassign`
    - **reassign_to_department_id** (query): target department UUID for employee reassignment

    ### Output
    - **204 No Content**
    """
    await Managers.departments.delete_department(
        session=session,
        department_id=department_id,
        mode=mode,
        reassign_to_department_id=reassign_to_department_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
