from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.employee.services.admin_employee_service import EmployeeService
from modules.employee.dto.admin_employee_dto import (
    EmployeePageRequest,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from utils.i18n import t
from typing import List

router = APIRouter(prefix="/employees")

# helper to check admin role

def ensure_admin(user: User, locale: str | None = None):
    if not any(r.code == "ADMIN" for r in user.roles):
        raise HTTPException(status_code=403, detail=t('forbidden', locale))

@router.post("/pagination")
def paginate(req: EmployeePageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    total, items = service.list_employees(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    # convert to output
    results = []
    for e in items:
        results.append({
            "id": e.id,
            "code": e.code,
            "name": e.full_name,
            "email": e.user.email if e.user else None,
            "phone": e.phone,
            "description": e.description,
            "is_active": e.is_active,
            "roles": [r.code for r in e.user.roles] if e.user else [],
        })
    return {"content": results, "totalElements": total}

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    emps = service.list_all_active()
    return [{"id": e.id, "code": e.code, "name": e.full_name} for e in emps]

@router.post("/")
def create(emp: EmployeeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    try:
        e = service.create_employee(emp.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"message": t('create_success', accept_language)}

@router.put("/{emp_id}")
def update(emp_id: str, emp: EmployeeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    try:
        e = service.update_employee(emp_id, emp.dict())
        if not e:
            raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"message": t('update_success', accept_language)}

@router.get("/{emp_id}")
def detail(emp_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    e = service.get_employee(emp_id)
    if not e:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {
        "id": e.id,
        "code": e.code,
        "name": e.full_name,
        "email": e.user.email if e.user else None,
        "phone": e.phone,
        "description": e.description,
        "is_active": e.is_active,
        "roles": [r.code for r in e.user.roles] if e.user else [],
    }

@router.post("/deactivate/{emp_id}")
def deactivate(emp_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    e = service.deactivate_employee(emp_id)
    if not e:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {"message": t('deactivate_success', accept_language)}

@router.post("/activate/{emp_id}")
def activate(emp_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    e = service.activate_employee(emp_id)
    if not e:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {"message": t('activate_success', accept_language)}

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = EmployeeService(db)
    emps = service.list_all_active()
    return [{"id": e.id, "name": e.full_name} for e in emps]
