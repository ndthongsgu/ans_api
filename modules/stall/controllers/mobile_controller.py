from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.controllers.mobile_controller import get_current_user
from modules.stall.services.mobile_service import StallMobileService
from models.user import User
from common.dto.response import success_response
from typing import Optional

router = APIRouter(prefix="/stalls")


@router.get("/")
def list_stalls(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: Optional[str] = Header(None),
    search: Optional[str] = None
):
    """Get all stalls with multilingual translations, optionally filtered by name"""
    # Parse Accept-Language header, fallback to user preference, then to 'vi'
    user_lang = accept_language.split(',')[0] if accept_language else (current_user.preferred_language or "vi")
    service = StallMobileService(db)
    results = service.list_stalls(user_lang, search)
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=results
    )


@router.get("/{stall_id}")
def get_stall_detail(
    stall_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: Optional[str] = Header(None)
):
    """Get stall detail with multilingual translations"""
    user_lang = accept_language.split(',')[0] if accept_language else (current_user.preferred_language or "vi")
    service = StallMobileService(db)
    data = service.get_stall(stall_id, user_lang)
    
    if not data:
        raise HTTPException(status_code=404, detail="Quán ăn không tồn tại")
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )


@router.get("/{stall_id}/nearby")
def get_nearby_stalls(
    stall_id: str,
    distance_km: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: Optional[str] = Header(None)
):
    """Get stalls nearby with multilingual translations"""
    user_lang = accept_language.split(',')[0] if accept_language else (current_user.preferred_language or "vi")
    service = StallMobileService(db)
    nearby = service.get_nearby_stalls(stall_id, user_lang)
    
    if nearby is None:
        raise HTTPException(status_code=404, detail="Quán ăn không tồn tại")
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=nearby
    )
