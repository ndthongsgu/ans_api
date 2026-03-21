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
from common.dto.response import success_response
from typing import List

router = APIRouter(prefix="/stall-contents")

# Helper to check if user is admin
def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

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
            "stall_name": c.stall.name if c.stall else None,
            "language_code": c.language_code,
            "audio_url": c.audio_url,
            "audio_duration": c.audio_duration,
            "audio_file_size": c.audio_file_size,
            "tts_script": c.tts_script,
            "version": c.version,
            "is_deleted": c.is_deleted,
        })
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    contents = service.list_all_active()
    data = [{"id": c.id, "stall_id": c.stall_id} for c in contents]
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    data = service.list_for_select()
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/")
def create(content: StallContentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    try:
        # Validate that either audio_url or tts_script is provided
        if not content.audio_url and not content.tts_script:
            raise RuntimeError("Either audio_url or tts_script must be provided")
        
        c = service.create_stall_content(content.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Tạo nội dung cửa hàng thành công",
        status_code=201
    )

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
    return success_response(
        message="Cập nhật nội dung cửa hàng thành công"
    )

@router.get("/{content_id}")
def detail(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.get_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    data = {
        "id": c.id,
        "stall_id": c.stall_id,
        "stall": {
            "id": c.stall.id,
            "name": c.stall.name,
        } if c.stall else None,
        "language_code": c.language_code,
        "audio_url": c.audio_url,
        "audio_duration": c.audio_duration,
        "audio_file_size": c.audio_file_size,
        "tts_script": c.tts_script,
        "version": c.version,
        "is_deleted": c.is_deleted,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
    }
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/deactivate/{content_id}")
def deactivate(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.deactivate_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Ngưng hoạt động nội dung cửa hàng thành công"
    )

@router.post("/activate/{content_id}")
def activate(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.activate_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Kích hoạt nội dung cửa hàng thành công"
    )
