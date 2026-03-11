from app.managers.departments import DepartmentManager
from app.managers.employees import EmployeeManager


class Managers:
    departments: DepartmentManager = DepartmentManager()
    employees: EmployeeManager = EmployeeManager()
