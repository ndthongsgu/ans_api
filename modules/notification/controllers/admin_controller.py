from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.notification.services.admin_service import NotificationService
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from models.notificationTranslation import NotificationTranslation
from common.dto.response import success_response
from typing import List

router = APIRouter(prefix="/notifications")


def ensure_admin(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")


@router.post("/pagination")
def paginate(
    page: int = 0,
    size: int = 20,
    user_id: str = None,
    notification_type: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated notifications (admin only, Vietnamese)"""
    ensure_admin(current_user)

    service = NotificationService(db)
    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if notification_type:
        filters['type'] = notification_type

    total, items = service.list_notifications(filters, page, size, sortBy='sent_at', sortDirection='DESC')

    results = []
    for n in items:
        # Get Vietnamese translation
        vi_trans = db.query(NotificationTranslation).filter(
            NotificationTranslation.notification_id == n.id,
            NotificationTranslation.language_code == "vi"
        ).first()

        results.append({
            "id": n.id,
            "user_id": n.user_id,
            "title": vi_trans.title if vi_trans else n.title,
            "message": vi_trans.message if vi_trans else n.message,
            "type": n.type,
            "is_read": n.is_read,
            "sent_at": n.sent_at,
            "read_at": n.read_at,
            "translation": vi_trans.dict(exclude={"id", "notification_id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted", "version"}) if vi_trans else None,
        })

    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )


@router.get("/{notification_id}")
def get_notification_detail(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification detail (admin only, Vietnamese)"""
    ensure_admin(current_user)

    service = NotificationService(db)
    notification = service.get_notification(notification_id)

    if not notification:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")

    # Get Vietnamese translation
    vi_trans = db.query(NotificationTranslation).filter(
        NotificationTranslation.notification_id == notification.id,
        NotificationTranslation.language_code == "vi"
    ).first()

    data = {
        "id": notification.id,
        "user_id": notification.user_id,
        "title": vi_trans.title if vi_trans else notification.title,
        "message": vi_trans.message if vi_trans else notification.message,
        "type": notification.type,
        "data": notification.data,
        "is_read": notification.is_read,
        "sent_at": notification.sent_at,
        "read_at": notification.read_at,
        "translation": vi_trans.dict(exclude={"id", "notification_id", "created_at", "updated_at", "created_by", "updated_by", "is_deleted", "version"}) if vi_trans else None,
    }

    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )


@router.post("/")
def create_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "system",
    data: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create notification (admin only, Vietnamese only)"""
    ensure_admin(current_user)

    service = NotificationService(db)
    try:
        notification = service.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data
        )

        return success_response(
            message="Tạo thông báo thành công",
            data={
                "id": notification.id,
                "user_id": notification.user_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "sent_at": notification.sent_at,
            },
            status_code=201
        )
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
