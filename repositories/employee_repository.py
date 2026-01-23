from sqlalchemy.orm import Session
from models.employee import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate

class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_employee(self, employee_id: str):
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_employees(self, skip: int = 0, limit: int = 100):
        return self.db.query(Employee).offset(skip).limit(limit).all()

    def create_employee(self, employee: EmployeeCreate):
        db_employee = Employee(user_id=employee.user_id, full_name=employee.full_name, phone=employee.phone, position=employee.position)
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee

    def update_employee(self, employee_id: str, employee: EmployeeUpdate):
        db_employee = self.get_employee(employee_id)
        if db_employee:
            db_employee.user_id = employee.user_id
            db_employee.full_name = employee.full_name
            db_employee.phone = employee.phone
            db_employee.position = employee.position
            self.db.commit()
            self.db.refresh(db_employee)
        return db_employee

    def delete_employee(self, employee_id: str):
        db_employee = self.get_employee(employee_id)
        if db_employee:
            self.db.delete(db_employee)
            self.db.commit()
        return db_employee
