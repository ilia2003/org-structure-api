from uuid import UUID

import sqlalchemy as sa

from app.db.crud.base import BaseCRUD
from app.db.models.employees import Employee


class EmployeeCRUD(BaseCRUD[Employee]):
    model = Employee

    async def list_by_department_id(self, department_id: UUID) -> list[Employee]:
        query = (
            sa.select(self.model)
            .where(self.model.department_id == department_id)
            .order_by(self.model.full_name.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def reassign_department(self, from_department_id: UUID, to_department_id: UUID) -> None:
        query = (
            sa.update(self.model)
            .where(self.model.department_id == from_department_id)
            .values(department_id=to_department_id)
        )
        await self.session.execute(query)
        await self.session.flush()
