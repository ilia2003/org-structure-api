from datetime import UTC, datetime
from uuid import uuid4

import factory

from app.db.models.departments import Department


class DepartmentFactory(factory.Factory):
    class Meta:
        model = Department

    id = factory.LazyFunction(uuid4)
    created_at = factory.LazyFunction(lambda: datetime.now(tz=UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(tz=UTC))
    name = factory.Sequence(lambda n: f"Department #{n}")
    parent_id = None
