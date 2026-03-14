from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.stall.services.admin_service import StallService
from modules.stall.dto.admin_dto import (
    StallPageRequest,
    StallCreate,
    StallUpdate,
    StallOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from utils.i18n import t
from typing import List

router = APIRouter(prefix="/stalls")

# Helper to check admin role
def ensure_admin(user: User, locale: str | None = None):
    if not any(r.code == "ADMIN" for r in user.roles):
        raise HTTPException(status_code=403, detail=t('forbidden', locale))

@router.post("/pagination")
def paginate(req: StallPageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    total, items = service.list_stalls(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for s in items:
        results.append({
            "id": s.id,
            "owner_id": s.owner_id,
            "name": s.name,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "radius": s.radius,
            "cover_image": s.cover_image,
            "status": s.status,
            "category": s.category,
            "price_range": s.price_range,
            "opening_hours": s.opening_hours,
            "contact_phone": s.contact_phone,
            "website": s.website,
            "average_rating": s.average_rating,
            "total_reviews": s.total_reviews,
        })
    return {"content": results, "totalElements": total}

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    stalls = service.list_all_active()
    return [{"id": s.id, "name": s.name, "owner_id": s.owner_id} for s in stalls]

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    return service.list_for_select()

@router.post("/")
def create(stall: StallCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    try:
        s = service.create_stall(stall.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"message": t('create_success', accept_language)}

@router.put("/{stall_id}")
def update(stall_id: str, stall: StallUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    try:
        s = service.update_stall(stall_id, stall.dict())
        if not s:
            raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"message": t('update_success', accept_language)}

@router.get("/{stall_id}")
def detail(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    s = service.get_stall(stall_id)
    if not s:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {
        "id": s.id,
        "owner_id": s.owner_id,
        "name": s.name,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "radius": s.radius,
        "cover_image": s.cover_image,
        "status": s.status,
        "category": s.category,
        "price_range": s.price_range,
        "opening_hours": s.opening_hours,
        "contact_phone": s.contact_phone,
        "website": s.website,
        "average_rating": s.average_rating,
        "total_reviews": s.total_reviews,
    }

@router.post("/deactivate/{stall_id}")
def deactivate(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    s = service.deactivate_stall(stall_id)
    if not s:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {"message": t('deactivate_success', accept_language)}

@router.post("/activate/{stall_id}")
def activate(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    s = service.activate_stall(stall_id)
    if not s:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {"message": t('activate_success', accept_language)}
