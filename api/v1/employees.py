from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.employee_service import EmployeeService
from schemas.employee import Employee, EmployeeCreate, EmployeeUpdate

router = APIRouter()

@router.post("/employees/", response_model=Employee)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.create_employee(employee)

@router.get("/employees/", response_model=list[Employee])
def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    return service.get_employees(skip=skip, limit=limit)

@router.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    db_employee = service.get_employee(employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: str, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    db_employee = service.update_employee(employee_id, employee)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    service = EmployeeService(db)
    db_employee = service.delete_employee(employee_id)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"detail": "Deleted"}
