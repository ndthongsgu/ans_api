from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.stallContent.services.admin_service import StallContentService
from modules.stallContent.dto.admin_dto import (
    StallContentPageRequest,
    StallContentCreate,
    StallContentUpdate,
    StallContentOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from utils.i18n import t
from typing import List

router = APIRouter(prefix="/stall-contents")

# Helper to check admin role
def ensure_admin(user: User, locale: str | None = None):
    if not any(r.code == "ADMIN" for r in user.roles):
        raise HTTPException(status_code=403, detail=t('forbidden', locale))

@router.post("/pagination")
def paginate(req: StallContentPageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    total, items = service.list_stall_contents(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for c in items:
        results.append({
            "id": c.id,
            "stall_id": c.stall_id,
            "language_code": c.language_code,
            "title": c.title,
            "description": c.description,
            "short_description": c.short_description,
            "audio_url": c.audio_url,
            "audio_duration": c.audio_duration,
            "audio_file_size": c.audio_file_size,
            "tts_script": c.tts_script,
            "version": c.version,
            "is_active": not c.is_deleted,
        })
    return {"content": results, "totalElements": total}

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    contents = service.list_all_active()
    return [{"id": c.id, "title": c.title, "stall_id": c.stall_id} for c in contents]

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    return service.list_for_select()

@router.post("/")
def create(content: StallContentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    try:
        c = service.create_stall_content(content.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Tạo thành công", "statusCode": 201}

@router.put("/{content_id}")
def update(content_id: str, content: StallContentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    try:
        c = service.update_stall_content(content_id, content.dict())
        if not c:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return {"success": True, "message": "Cập nhật thành công", "statusCode": 200}

@router.get("/{content_id}")
def detail(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.get_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail=t('not_found', accept_language))
    return {
        "id": c.id,
        "stall_id": c.stall_id,
        "language_code": c.language_code,
        "title": c.title,
        "description": c.description,
        "short_description": c.short_description,
        "audio_url": c.audio_url,
        "audio_duration": c.audio_duration,
        "audio_file_size": c.audio_file_size,
        "tts_script": c.tts_script,
        "version": c.version,
        "is_active": not c.is_deleted,
    }

@router.post("/deactivate/{content_id}")
def deactivate(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.deactivate_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Ngưng hoạt động thành công", "statusCode": 200}

@router.post("/activate/{content_id}")
def activate(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.activate_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return {"success": True, "message": "Kích hoạt thành công", "statusCode": 200}