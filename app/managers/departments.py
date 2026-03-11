from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.departments import DepartmentCRUD
from app.dependencies.exceptions import RequestedDataNotFoundException, BadRequestException, ConflictException
from app.managers.utils import build_department_tree, check_no_cycle, check_target_not_in_subtree
from app.schemas.departments import (
    DepartmentCreateSchema,
    DepartmentSchema,
    DepartmentTreeSchema,
    DepartmentUpdateSchema,
)


class DepartmentManager:
    """Business logic for departments."""

    @staticmethod
    async def create_department(
        session: AsyncSession,
        data: DepartmentCreateSchema,
    ) -> DepartmentSchema:
        departments_db = DepartmentCRUD(session)

        if data.parent_id is not None:
            parent = await departments_db.get_one(id=data.parent_id)
            if not parent:
                raise RequestedDataNotFoundException("Parent department not found")

        duplicate = await departments_db.get_one(
            name=data.name,
            parent_id=data.parent_id,
        )
        if duplicate:
            raise ConflictException("Department with this name already exists")

        department = await departments_db.create(**data.model_dump())
        await session.commit()
        return DepartmentSchema.model_validate(department)

    @staticmethod
    async def get_department(
        session: AsyncSession,
        department_id: UUID,
        depth: int = 1,
        include_employees: bool = True,
    ) -> DepartmentTreeSchema:
        departments_db = DepartmentCRUD(session)

        department = await departments_db.get_one(id=department_id)
        if not department:
            raise RequestedDataNotFoundException("Department not found")

        return await build_department_tree(
            session=session,
            department=department,
            depth=depth,
            include_employees=include_employees,
        )

    @staticmethod
    async def update_department(
        session: AsyncSession,
        department_id: UUID,
        data: DepartmentUpdateSchema,
    ) -> DepartmentSchema:
        departments_db = DepartmentCRUD(session)

        department = await departments_db.get_one(id=department_id)
        if not department:
            raise RequestedDataNotFoundException("Department not found")

        update_data = data.model_dump(exclude_unset=True)

        if "parent_id" in update_data:
            new_parent_id = update_data["parent_id"]

            if new_parent_id == department.id:
                raise ConflictException("Department cannot be parent of itself")

            if new_parent_id is not None:
                parent = await departments_db.get_one(id=new_parent_id)
                if not parent:
                    raise RequestedDataNotFoundException("Parent department not found")

                await check_no_cycle(
                    session=session,
                    department_id=department.id,
                    new_parent_id=new_parent_id,
                )

        new_name = update_data.get("name", department.name)
        new_parent_id = update_data.get("parent_id", department.parent_id)

        duplicate = await departments_db.get_one(
            name=new_name,
            parent_id=new_parent_id,
        )
        if duplicate and duplicate.id != department.id:
            raise ConflictException("Department with this name already exists")

        updated_department = await departments_db.update(department, **update_data)
        await session.commit()
        return DepartmentSchema.model_validate(updated_department)

    @staticmethod
    async def delete_department(
        session: AsyncSession,
        department_id: UUID,
        mode: str,
        reassign_to_department_id: UUID | None = None,
    ) -> None:
        from app.db.crud.employees import EmployeeCRUD

        departments_db = DepartmentCRUD(session)
        employees_db = EmployeeCRUD(session)

        department = await departments_db.get_one(id=department_id)
        if not department:
            raise RequestedDataNotFoundException("Department not found")

        if mode == "cascade":
            await departments_db.delete(department)
            await session.commit()
            return

        if mode != "reassign":
            raise BadRequestException("Unsupported delete mode")

        if reassign_to_department_id is None:
            raise BadRequestException("reassign_to_department_id is required")

        if reassign_to_department_id == department_id:
            raise ConflictException("Cannot reassign employees to the same department")

        target_department = await departments_db.get_one(id=reassign_to_department_id)
        if not target_department:
            raise RequestedDataNotFoundException("Target department not found")

        await check_target_not_in_subtree(
            session=session,
            department_id=department_id,
            target_department_id=reassign_to_department_id,
        )

        employees = await employees_db.get_all(department_id=department_id)
        for employee in employees:
            await employees_db.update(employee, department_id=reassign_to_department_id)

        await departments_db.delete(department)
        await session.commit()