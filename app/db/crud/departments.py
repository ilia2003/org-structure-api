from uuid import UUID

import sqlalchemy as sa

from app.db.crud.base import BaseCRUD
from app.db.models.departments import Department


class DepartmentCRUD(BaseCRUD[Department]):
    model = Department

    async def get_children(self, parent_id: UUID | None) -> list[Department]:
        query = (
            sa.select(self.model)
            .where(self.model.parent_id == parent_id)
            .order_by(self.model.name.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, department: Department, **values) -> Department:
        for field, value in values.items():
            setattr(department, field, value)

        await self.session.flush()
        await self.session.refresh(department)
        return department
