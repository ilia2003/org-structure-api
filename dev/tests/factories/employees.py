from datetime import UTC, datetime
from uuid import uuid4

import factory

from app.db.models.employees import Employee


class EmployeeFactory(factory.Factory):
    class Meta:
        model = Employee

    id = factory.LazyFunction(uuid4)
    created_at = factory.LazyFunction(lambda: datetime.now(tz=UTC))
    updated_at = factory.LazyFunction(lambda: datetime.now(tz=UTC))
    full_name = factory.Sequence(lambda n: f"Employee #{n}")
    position = factory.Sequence(lambda n: f"Position #{n}")
    hired_at = None
    department_id = None
