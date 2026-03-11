from app.db.crud.base import BaseCRUD
from app.db.models.employees import Employee


class EmployeeCRUD(BaseCRUD[Employee]):
    model = Employee