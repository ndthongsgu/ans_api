from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from modules.notification.services.mobile_service import NotificationMobileService
from modules.auth.controllers.mobile_controller import get_current_user
from models.user import User
from common.dto.response import success_response

router = APIRouter(prefix="/notifications")


@router.get("/")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications with multilingual translation"""
    user_lang = current_user.preferred_language or "vi"
    service = NotificationMobileService(db)
    results = service.get_user_notifications(current_user.id, user_lang)
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=results
    )


@router.get("/{notification_id}")
def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification detail with multilingual translation"""
    user_lang = current_user.preferred_language or "vi"
    service = NotificationMobileService(db)
    data = service.get_notification(notification_id, current_user.id, user_lang)
    
    if not data:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )


@router.post("/{notification_id}/mark-as-read")
def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    service = NotificationMobileService(db)
    success = service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")
    
    return success_response(
        message="Đánh dấu thông báo đã đọc"
    )


@router.post("/mark-all-as-read")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    service = NotificationMobileService(db)
    service.mark_all_as_read(current_user.id)
    
    return success_response(
        message="Đánh dấu tất cả thông báo đã đọc"
    )


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread notification count"""
    service = NotificationMobileService(db)
    count = service.get_unread_count(current_user.id)
    
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"unread_count": count}
    )
