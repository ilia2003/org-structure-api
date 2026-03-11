from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.departments import DepartmentCRUD
from app.db.crud.employees import EmployeeCRUD
from app.dependencies.exceptions.http import ConflictException
from app.schemas.departments import DepartmentSchema, DepartmentTreeSchema
from app.schemas.employees import EmployeeSchema


async def build_department_tree(
    session: AsyncSession,
    department,
    depth: int,
    include_employees: bool,
) -> DepartmentTreeSchema:
    departments_db = DepartmentCRUD(session)
    employees_db = EmployeeCRUD(session)

    employees = []
    if include_employees:
        employee_models = await employees_db.get_all(department_id=department.id)
        employee_models = sorted(employee_models, key=lambda item: item.full_name.lower())
        employees = [EmployeeSchema.model_validate(employee) for employee in employee_models]

    children = []
    if depth > 0:
        child_models = await departments_db.get_all(parent_id=department.id)
        child_models = sorted(child_models, key=lambda item: item.name.lower())

        for child in child_models:
            children.append(
                await build_department_tree(
                    session=session,
                    department=child,
                    depth=depth - 1,
                    include_employees=include_employees,
                )
            )

    return DepartmentTreeSchema(
        department=DepartmentSchema.model_validate(department),
        employees=employees,
        children=children,
    )


async def check_no_cycle(
    session: AsyncSession,
    department_id: UUID,
    new_parent_id: UUID,
) -> None:
    departments_db = DepartmentCRUD(session)
    current_parent_id = new_parent_id

    while current_parent_id is not None:
        if current_parent_id == department_id:
            raise ConflictException("Cycle detected in department tree")

        parent = await departments_db.get_one(id=current_parent_id)
        if not parent:
            break

        current_parent_id = parent.parent_id


async def check_target_not_in_subtree(
    session: AsyncSession,
    department_id: UUID,
    target_department_id: UUID,
) -> None:
    departments_db = DepartmentCRUD(session)
    children = await departments_db.get_all(parent_id=department_id)

    for child in children:
        if child.id == target_department_id:
            raise ConflictException("Cannot reassign employees to department subtree")

        await check_target_not_in_subtree(
            session=session,
            department_id=child.id,
            target_department_id=target_department_id,
        )
