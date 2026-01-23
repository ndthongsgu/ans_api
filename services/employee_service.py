from sqlalchemy.orm import Session
from repositories.employee_repository import EmployeeRepository
from schemas.employee import EmployeeCreate, EmployeeUpdate

class EmployeeService:
    def __init__(self, db: Session):
        self.repository = EmployeeRepository(db)

    def get_employee(self, employee_id: str):
        return self.repository.get_employee(employee_id)

    def get_employees(self, skip: int = 0, limit: int = 100):
        return self.repository.get_employees(skip, limit)

    def create_employee(self, employee: EmployeeCreate):
        return self.repository.create_employee(employee)

    def update_employee(self, employee_id: str, employee: EmployeeUpdate):
        return self.repository.update_employee(employee_id, employee)

    def delete_employee(self, employee_id: str):
        return self.repository.delete_employee(employee_id)
