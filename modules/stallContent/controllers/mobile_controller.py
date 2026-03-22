from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.controllers.mobile_controller import get_current_user
from modules.stallContent.services.mobile_service import StallContentMobileService
from models.user import User
from common.dto.response import success_response

router = APIRouter(prefix="/stall-contents")


@router.get("/{stall_id}")
def get_stall_contents(stall_id: str, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all contents for a stall in client's language"""
    # Get language from Accept-Language header, fallback to user preference or 'vi'
    accept_lang = request.headers.get('Accept-Language', '')
    user_lang = accept_lang.split(',')[0].split('-')[0] if accept_lang else (current_user.preferred_language or "vi")
    
    service = StallContentMobileService(db)
    results = service.get_stall_contents(stall_id, user_lang)
    
    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy nội dung cho quán này")
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=results
    )


@router.get("/{stall_id}/{language_code}")
def get_stall_content_by_language(stall_id: str, language_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get content for a stall in specific language"""
    service = StallContentMobileService(db)
    results = service.get_stall_contents(stall_id, language_code)
    
    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy nội dung cho quán này")
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=results
    )


@router.get("/{stall_id}/available-languages")
def get_available_languages(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get available languages for stall content"""
    service = StallContentMobileService(db)
    languages = service.get_available_languages(stall_id)
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"languages": languages, "total": len(languages)}
    )
