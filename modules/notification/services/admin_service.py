from sqlalchemy.orm import Session
from models.notification import Notification
from models.notificationTranslation import NotificationTranslation
import time
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def list_notifications(
        self,
        filters: dict,
        page: int,
        size: int,
        sortBy: str | None = None,
        sortDirection: str | None = None
    ) -> Tuple[int, List[Notification]]:
        """List notifications with pagination (admin view)"""
        q = self.db.query(Notification)

        if filters.get('user_id'):
            q = q.filter(Notification.user_id == filters['user_id'])

        if filters.get('type'):
            q = q.filter(Notification.type == filters['type'])

        if filters.get('is_read') is not None:
            q = q.filter(Notification.is_read == filters['is_read'])

        if filters.get('is_deleted') is not None:
            q = q.filter(Notification.is_deleted == filters['is_deleted'])

        # Ordering
        if sortBy:
            column = getattr(Notification, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
        else:
            # Default: order by sent_at DESC
            q = q.order_by(Notification.sent_at.desc())

        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_notification(self, notification_id: str):
        """Get single notification"""
        return self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

    def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "system",
        data: dict = None
    ):
        """
        Create notification with Vietnamese translation
        
        Only admin creates notifications in Vietnamese
        """
        if not user_id or not user_id.strip():
            raise RuntimeError("user_id is required")

        if not title or not title.strip():
            raise RuntimeError("title is required")

        if not message or not message.strip():
            raise RuntimeError("message is required")

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            data=data,
            is_read=False,
            sent_at=int(time.time())
        )

        self.db.add(notification)
        self.db.flush()  # Get notification ID

        # Create Vietnamese translation
        vi_translation = NotificationTranslation(
            notification_id=notification.id,
            language_code="vi",
            title=title,
            message=message,
        )
        self.db.add(vi_translation)

        self.db.commit()
        self.db.refresh(notification)

        logger.info(f"Created notification {notification.id} for user {user_id}")
        return notification

    def get_user_notifications(
        self,
        user_id: str,
        is_read: bool = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get user's notifications (mobile view)"""
        q = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_deleted == False
        )

        if is_read is not None:
            q = q.filter(Notification.is_read == is_read)

        return q.order_by(Notification.sent_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: str, user_id: str):
        """Mark notification as read by user"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return None

        notification.is_read = True
        notification.read_at = int(time.time())
        self.db.commit()

        logger.info(f"Marked notification {notification_id} as read for user {user_id}")
        return notification

    def mark_all_as_read(self, user_id: str):
        """Mark all user's notifications as read"""
        self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).update({
            Notification.is_read: True,
            Notification.read_at: int(time.time())
        })
        self.db.commit()
        logger.info(f"Marked all notifications as read for user {user_id}")

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).count()

    def delete_notification(self, notification_id: str):
        """Soft delete notification"""
        notification = self.get_notification(notification_id)
        if notification:
            notification.is_deleted = True
            self.db.commit()
            logger.info(f"Deleted notification {notification_id}")
        return notification

    def list_all_active(self):
        """Get all active notifications"""
        return self.db.query(Notification).filter(
            Notification.is_deleted == False
        ).all()

    def list_for_select(self):
        """Return notifications formatted for select dropdown"""
        notifications = self.list_all_active()
        return [
            {
                "id": n.id,
                "user_id": n.user_id,
                "title": n.title,
                "type": n.type,
            }
            for n in notifications
        ]
