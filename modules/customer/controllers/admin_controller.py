from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.customer.services.admin_service import CustomerService
from modules.customer.dto.admin_dto import (
    CustomerPageRequest,
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from common.dto.response import success_response
from typing import List

router = APIRouter(prefix="/customers")

# Helper to check if user is admin
def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

@router.post("/pagination")
def paginate(req: CustomerPageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    total, items = service.list_customers(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for c in items:
        results.append({
            "id": c.id,
            "name": c.full_name,
            "email": c.user.email if c.user else None,
            "phone": c.phone,
            "is_deleted": c.user.is_deleted if c.user else True,
            "roles": [r.code for r in c.user.roles] if c.user else [],
        })
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    customers = service.list_all_active()
    data = [{"id": c.id, "name": c.full_name, "phone": c.phone} for c in customers]
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    data = service.list_for_select()
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/")
def create(customer: CustomerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    try:
        c = service.create_customer(customer.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Tạo khách hàng thành công",
        status_code=201
    )

@router.put("/{customer_id}")
def update(customer_id: str, customer: CustomerUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    try:
        c = service.update_customer(customer_id, customer.dict())
        if not c:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Cập nhật khách hàng thành công"
    )

@router.get("/{customer_id}")
def detail(customer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    c = service.get_customer(customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    data = {
        "id": c.id,
        "name": c.full_name,
        "email": c.user.email if c.user else None,
        "phone": c.phone,
        "is_deleted": c.user.is_deleted if c.user else True,
        "roles": [r.code for r in c.user.roles] if c.user else [],
    }
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/deactivate/{customer_id}")
def deactivate(customer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    c = service.deactivate_customer(customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Ngưng hoạt động khách hàng thành công"
    )

@router.post("/activate/{customer_id}")
def activate(customer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    c = service.activate_customer(customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Kích hoạt khách hàng thành công"
    )

@router.delete("/{customer_id}")
def delete(customer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = CustomerService(db)
    result = service.delete_customer(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Xóa khách hàng thành công"
    )
