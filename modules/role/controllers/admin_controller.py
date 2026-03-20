from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.role.services.admin_service import RoleService
from modules.role.dto.admin_dto import (
    RolePageRequest,
    RoleCreate,
    RoleUpdate,
    RoleOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from utils.i18n import t
from typing import List

router = APIRouter(prefix="/roles")

# Helper to check admin role
def ensure_admin(user: User, locale: str | None = None):
    if not any(r.code == "ADMIN" for r in user.roles):
        raise HTTPException(status_code=403, detail=t('forbidden', locale))

@router.post("/pagination")
def paginate(req: RolePageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    total, items = service.list_roles(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for r in items:
        results.append({
            "id": r.id,
            "code": r.code,
            "name": r.name,
            "permissions": r.permissions,
        })
    return {"content": results, "totalElements": total}

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    roles = service.list_all_active()
    return [{"id": r.id, "code": r.code, "name": r.name} for r in roles]

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    return service.list_for_select()

@router.post("/")
def create(role: RoleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    try:
        r = service.create_role(role.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Tạo thành công", "statusCode": 201}

@router.put("/{role_id}")
def update(role_id: str, role: RoleUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    try:
        r = service.update_role(role_id, role.dict())
        if not r:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Cập nhật thành công", "statusCode": 200}

@router.get("/{role_id}")
def detail(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    r = service.get_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {
        "id": r.id,
        "code": r.code,
        "name": r.name,
        "permissions": r.permissions,
    }

@router.post("/deactivate/{role_id}")
def deactivate(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    r = service.deactivate_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Ngưng hoạt động thành công", "statusCode": 200}

@router.post("/activate/{role_id}")
def activate(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    r = service.activate_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Kích hoạt thành công", "statusCode": 200}