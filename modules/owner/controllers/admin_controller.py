from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.owner.services.admin_service import OwnerService
from modules.owner.dto.admin_dto import (
    OwnerPageRequest,
    OwnerCreate,
    OwnerUpdate,
    OwnerOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from common.dto.response import success_response
from typing import List

router = APIRouter(prefix="/owners")

# Helper to check if user is admin
def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

@router.post("/pagination")
def paginate(req: OwnerPageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    total, items = service.list_owners(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for o in items:
        results.append({
            "id": o.id,
            "name": o.full_name,
            "email": o.user.email if o.user else None,
            "phone": o.phone,
            "business_name": o.business_name,
            "business_address": o.business_address,
            "is_deleted": o.user.is_deleted if o.user else True,
            "roles": [r.code for r in o.user.roles] if o.user else [],
            "created_at": o.created_at,
        })
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    owners = service.list_all_active()
    data = [{"id": o.id, "name": o.full_name, "phone": o.phone} for o in owners]
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    data = service.list_for_select()
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/")
def create(owner: OwnerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    try:
        o = service.create_owner(owner.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Tạo chủ cửa hàng thành công",
        status_code=201
    )

@router.put("/{owner_id}")
def update(owner_id: str, owner: OwnerUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    try:
        o = service.update_owner(owner_id, owner.dict())
        if not o:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Cập nhật chủ cửa hàng thành công"
    )

@router.get("/{owner_id}")
def detail(owner_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    o = service.get_owner(owner_id)
    if not o:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    data = {
        "id": o.id,
        "name": o.full_name,
        "email": o.user.email if o.user else None,
        "phone": o.phone,
        "business_name": o.business_name,
        "business_address": o.business_address,
        "is_deleted": o.user.is_deleted if o.user else True,
        "roles": [r.code for r in o.user.roles] if o.user else [],
        "created_at": o.created_at,
    }
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/deactivate/{owner_id}")
def deactivate(owner_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    o = service.deactivate_owner(owner_id)
    if not o:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Ngưng hoạt động chủ cửa hàng thành công"
    )

@router.post("/activate/{owner_id}")
def activate(owner_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    o = service.activate_owner(owner_id)
    if not o:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Kích hoạt chủ cửa hàng thành công"
    )
