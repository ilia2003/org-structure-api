from typing import Any, Generic, TypeVar

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


ModelT = TypeVar("ModelT")


class BaseCRUD(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one(self, **filters: Any) -> ModelT | None:
        query = sa.select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, **filters: Any) -> list[ModelT]:
        query = sa.select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, **values: Any) -> ModelT:
        instance = self.model(**values)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, **values: Any) -> ModelT:
        for field, value in values.items():
            setattr(instance, field, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()
