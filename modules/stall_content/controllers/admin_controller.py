from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from models.stallContent import StallContent
from models.stallContentTranslation import StallContentTranslation
from modules.stall_content.services.admin_service import StallContentService
from modules.stall_content.dto.admin_dto import (
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
        # Get all translations for this content
        all_translations = db.query(StallContentTranslation).filter(
            StallContentTranslation.stall_content_id == c.id
        ).all()
        
        # Get Vietnamese translation for primary display
        vi_trans = next((t for t in all_translations if t.language_code == "vi"), None)
        
        results.append({
            "id": c.id,
            "stall_id": c.stall_id,
            "stall_name": c.stall.name if c.stall else None,
            "audio_url": vi_trans.audio_url if vi_trans else c.audio_url,
            "tts_script": vi_trans.tts_script if vi_trans else c.tts_script,
            "version": c.version,
            "is_deleted": c.is_deleted,
            "vi_trans": {
                "language_code": vi_trans.language_code,
                "audio_url": vi_trans.audio_url,
                "tts_script": vi_trans.tts_script,
            } if vi_trans else None,
            "translations": [
                {
                    "language_code": t.language_code,
                    "audio_url": t.audio_url,
                    "tts_script": t.tts_script,
                }
                for t in all_translations
            ]
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
        # User provides Vietnamese TTS script
        # Service will automatically create records for all languages
        if not content.tts_script:
            raise RuntimeError("tts_script is required (in Vietnamese)")
        
        created_contents = service.create_stall_content(content.dict())
        
        # Format response - only include translation records (skip base StallContent)
        created_data = []
        for c in created_contents:
            if isinstance(c, StallContentTranslation):
                created_data.append({
                    "id": c.id,
                    "stall_content_id": c.stall_content_id,
                    "language_code": c.language_code,
                    "audio_url": c.audio_url,
                    "tts_script": c.tts_script,
                })
        
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Tạo nội dung cửa hàng thành công (các bản dịch được tạo tự động)",
        data={"created_contents": created_data, "total_languages": len(created_data)},
        status_code=201
    )

@router.put("/{content_id}")
def update(content_id: str, content: StallContentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    try:
        # When user updates Vietnamese content with new tts_script
        # Service will update all language versions automatically
        updated_contents = service.update_stall_content(content_id, content.dict())
        
        if not updated_contents:
            raise HTTPException(status_code=404, detail="Không tìm thấy nội dung cho quán này")
        
        # Format response with translations for the first content record
        updated_data = []
        if updated_contents:
            content_record = updated_contents[0]
            all_translations = db.query(StallContentTranslation).filter(
                StallContentTranslation.stall_content_id == content_record.id
            ).all()
            for trans in all_translations:
                updated_data.append({
                    "language_code": trans.language_code,
                    "audio_url": trans.audio_url,
                    "tts_script": trans.tts_script,
                })
        
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Cập nhật nội dung cửa hàng thành công (tất cả ngôn ngữ được cập nhật)",
        data={"updated_contents": updated_data, "total_languages": len(updated_data)}
    )

@router.get("/{stall_id}/detail")
def detail_by_stall(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    
    # Get all content records for this stall
    contents = db.query(StallContent).filter(StallContent.stall_id == stall_id).all()
    
    if not contents:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    
    data = []
    for c in contents:
        # Get all translations for this content
        all_translations = db.query(StallContentTranslation).filter(
            StallContentTranslation.stall_content_id == c.id
        ).all()
        
        # Get Vietnamese translation for primary display
        vi_trans = next((t for t in all_translations if t.language_code == "vi"), None)
        
        data.append({
            "id": c.id,
            "stall_id": c.stall_id,
            "stall": {
                "id": c.stall.id,
                "name": c.stall.name,
            } if c.stall else None,
            "audio_url": vi_trans.audio_url if vi_trans else c.audio_url,
            "audio_duration": c.audio_duration,
            "audio_file_size": c.audio_file_size,
            "tts_script": vi_trans.tts_script if vi_trans else c.tts_script,
            "version": c.version,
            "is_deleted": c.is_deleted,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "vi_trans": {
                "language_code": vi_trans.language_code,
                "audio_url": vi_trans.audio_url,
                "tts_script": vi_trans.tts_script,
            } if vi_trans else None,
            "translations": [
                {
                    "language_code": t.language_code,
                    "audio_url": t.audio_url,
                    "tts_script": t.tts_script,
                }
                for t in all_translations
            ]
        })
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"contents": data, "total_languages": len(data)}
    )

@router.get("/{content_id}")
def detail(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallContentService(db)
    c = service.get_stall_content(content_id)
    if not c:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    
    # Get all translations for this content
    all_translations = db.query(StallContentTranslation).filter(
        StallContentTranslation.stall_content_id == c.id
    ).all()
    
    # Get Vietnamese translation for primary display
    vi_trans = next((t for t in all_translations if t.language_code == "vi"), None)
    
    data = {
        "id": c.id,
        "stall_id": c.stall_id,
        "stall": {
            "id": c.stall.id,
            "name": c.stall.name,
        } if c.stall else None,
        "audio_url": vi_trans.audio_url if vi_trans else c.audio_url,
        "tts_script": vi_trans.tts_script if vi_trans else c.tts_script,
        "version": c.version,
        "is_deleted": c.is_deleted,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "vi_trans": {
            "language_code": vi_trans.language_code,
            "audio_url": vi_trans.audio_url,
            "tts_script": vi_trans.tts_script,
        } if vi_trans else None,
        "translations": [
            {
                "language_code": t.language_code,
                "audio_url": t.audio_url,
                "tts_script": t.tts_script,
            }
            for t in all_translations
        ]
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
