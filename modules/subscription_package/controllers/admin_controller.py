from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.subscription_package.services.admin_service import SubscriptionPackageService
from modules.subscription_package.dto.admin_dto import (
    SubscriptionPackagePageRequest,
    SubscriptionPackageCreate,
    SubscriptionPackageUpdate,
    SubscriptionPackageOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from utils.i18n import t
from typing import List

router = APIRouter(prefix="/subscription-packages")

# Helper to check admin role
def ensure_admin(user: User, locale: str | None = None):
    if not any(r.code == "ADMIN" for r in user.roles):
        raise HTTPException(status_code=403, detail=t('forbidden', locale))

@router.post("/pagination")
def paginate(req: SubscriptionPackagePageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    total, items = service.list_subscription_packages(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for p in items:
        results.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "duration": p.duration,
            "max_stalls": p.max_stalls,
            "max_audio_storage": p.max_audio_storage,
            "features": p.features,
            "is_deleted": p.is_deleted,
        })
    return {"content": results, "totalElements": total}

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    packages = service.list_all_active()
    return [{"id": p.id, "name": p.name, "price": p.price} for p in packages]

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    return service.list_for_select()

@router.post("/")
def create(package: SubscriptionPackageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    try:
        p = service.create_subscription_package(package.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Tạo thành công", "statusCode": 201}

@router.put("/{package_id}")
def update(package_id: str, package: SubscriptionPackageUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    try:
        p = service.update_subscription_package(package_id, package.dict())
        if not p:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Cập nhật thành công", "statusCode": 200}

@router.get("/{package_id}")
def detail(package_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    p = service.get_subscription_package(package_id)
    if not p:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "duration": p.duration,
        "max_stalls": p.max_stalls,
        "max_audio_storage": p.max_audio_storage,
        "features": p.features,
        "is_deleted": p.is_deleted,
    }

@router.post("/deactivate/{package_id}")
def deactivate(package_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    p = service.deactivate_subscription_package(package_id)
    if not p:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Ngưng hoạt động thành công", "statusCode": 200}

@router.post("/activate/{package_id}")
def activate(package_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    p = service.activate_subscription_package(package_id)
    if not p:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Kích hoạt thành công", "statusCode": 200}