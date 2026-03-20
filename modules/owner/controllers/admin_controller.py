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
from utils.i18n import t
from typing import List

router = APIRouter(prefix="/owners")

# Helper to check if user is admin
def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail=t('forbidden', locale))

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
    return {"content": results, "totalElements": total}

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    owners = service.list_all_active()
    return [{"id": o.id, "name": o.full_name, "phone": o.phone} for o in owners]

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    return service.list_for_select()

@router.post("/")
def create(owner: OwnerCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    try:
        o = service.create_owner(owner.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Tạo thành công", "statusCode": 201}

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
    return {"success": True, "message": "Cập nhật thành công", "statusCode": 200}

@router.get("/{owner_id}")
def detail(owner_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    o = service.get_owner(owner_id)
    if not o:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {
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

@router.post("/deactivate/{owner_id}")
def deactivate(owner_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    o = service.deactivate_owner(owner_id)
    if not o:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Ngưng hoạt động thành công", "statusCode": 200}

@router.post("/activate/{owner_id}")
def activate(owner_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = OwnerService(db)
    o = service.activate_owner(owner_id)
    if not o:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Kích hoạt thành công", "statusCode": 200}