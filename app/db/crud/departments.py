from app.db.crud.base import BaseCRUD
from app.db.models.departments import Department


class DepartmentCRUD(BaseCRUD[Department]):
    model = Department
