import json
from fastapi import APIRouter, Depends, HTTPException, Header, Request
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
from utils.action_log_helper import log_action
from common.dto.response import success_response
from typing import List

router = APIRouter(prefix="/roles")


def parse_permissions(value):
    if value is None:
        return []

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else [str(parsed)]
        except ValueError:
            return [item.strip() for item in value.split(",") if item.strip()]

    if isinstance(value, list):
        return value

    return [str(value)]


# Helper to check if user is admin
def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

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
            "is_deleted": r.is_deleted,
            "description": r.description,
            "permissions": parse_permissions(r.permissions),
        })
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    roles = service.list_all_active()
    data = [{"id": r.id, "code": r.code, "name": r.name} for r in roles]
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    data = service.list_for_select()
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/")
def create(role: RoleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None, accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    try:
        r = service.create_role(role.dict())
        # Log the action
        log_action(
            db=db,
            function_type="Roles",
            function_id=r.id,
            action="Create",
            user_id=current_user.id,
            change_details=f"Created role: {r.code} - {r.name}",
            new_values={"code": r.code, "name": r.name, "permissions": r.permissions},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Tạo vai trò thành công",
        status_code=201
    )

@router.put("/{role_id}")
def update(role_id: str, role: RoleUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None, accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    
    # Get old values before update
    old_role = service.get_role(role_id)
    old_values = None
    if old_role:
        old_values = {
            "code": old_role.code,
            "name": old_role.name,
            "permissions": old_role.permissions,
        }
    
    try:
        r = service.update_role(role_id, role.dict())
        if not r:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
        
        # Log the action
        log_action(
            db=db,
            function_type="Roles",
            function_id=role_id,
            action="Update",
            user_id=current_user.id,
            change_details=f"Updated role: {r.code}",
            old_values=old_values,
            new_values={"code": r.code, "name": r.name, "permissions": r.permissions},
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Cập nhật vai trò thành công"
    )

@router.get("/{role_id}")
def detail(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    r = service.get_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    data = {
        "id": r.id,
        "code": r.code,
        "name": r.name,
        "permissions": parse_permissions(r.permissions),
    }
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/deactivate/{role_id}")
def deactivate(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None, accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    r = service.deactivate_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    
    # Log the action
    log_action(
        db=db,
        function_type="Roles",
        function_id=role_id,
        action="Deactivate",
        user_id=current_user.id,
        change_details=f"Deactivated role: {r.code}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    
    return success_response(
        message="Ngưng hoạt động vai trò thành công"
    )

@router.post("/activate/{role_id}")
def activate(role_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), request: Request = None, accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = RoleService(db)
    r = service.activate_role(role_id)
    if not r:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    
    # Log the action
    log_action(
        db=db,
        function_type="Roles",
        function_id=role_id,
        action="Activate",
        user_id=current_user.id,
        change_details=f"Activated role: {r.code}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
    )
    
    return success_response(
        message="Kích hoạt vai trò thành công"
    )
