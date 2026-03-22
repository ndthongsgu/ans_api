from sqlalchemy.orm import Session
from common.enums.language import LanguageCode
from models.notification import Notification
from models.notificationTranslation import NotificationTranslation
from models.user import User
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationMobileService:
    """Service for mobile API - read-only notifications with multilingual support"""
    
    def __init__(self, db: Session):
        self.db = db

    def _get_notification_translation(self, notification_id: str, language_code: str) -> NotificationTranslation | None:
        """Get translation for specific language, fallback to default language if not found"""
        trans = self.db.query(NotificationTranslation).filter(
            NotificationTranslation.notification_id == notification_id,
            NotificationTranslation.language_code == language_code
        ).first()
        
        if not trans and language_code != LanguageCode.DEFAULT:
            # Fallback to default language
            trans = self.db.query(NotificationTranslation).filter(
                NotificationTranslation.notification_id == notification_id,
                NotificationTranslation.language_code == LanguageCode.DEFAULT
            ).first()
        
        return trans

    def get_user_notifications(self, user_id: str, language_code: str = "vi") -> List[dict]:
        """Get all notifications for a user with multilingual translations"""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_deleted == False
        ).order_by(Notification.created_at.desc()).all()
        
        results = []
        for n in notifications:
            trans = self._get_notification_translation(n.id, language_code)
            
            results.append({
                "id": n.id,
                "user_id": n.user_id,
                "type": n.type,
                "title": trans.title if trans else n.title,
                "message": trans.message if trans else n.message,
                "is_read": n.is_read,
                "related_entity_id": n.related_entity_id,
                "created_at": n.created_at,
                "read_at": n.read_at,
                "language_code": language_code,
            })
        
        logger.info(f"Retrieved {len(results)} notifications for user {user_id} in language {language_code}")
        return results

    def get_notification(self, notification_id: str, user_id: str, language_code: str = "vi") -> dict | None:
        """Get single notification detail with multilingual translation"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
            Notification.is_deleted == False
        ).first()
        
        if not notification:
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            return None
        
        trans = self._get_notification_translation(notification.id, language_code)
        
        data = {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": trans.title if trans else notification.title,
            "message": trans.message if trans else notification.message,
            "is_read": notification.is_read,
            "related_entity_id": notification.related_entity_id,
            "created_at": notification.created_at,
            "read_at": notification.read_at,
            "language_code": language_code,
        }
        
        logger.info(f"Retrieved notification {notification_id} for user {user_id}")
        return data

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a single notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            logger.warning(f"Notification {notification_id} not found for user {user_id}")
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Marked notification {notification_id} as read for user {user_id}")
        return True

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()
        
        count = len(notifications)
        
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).count()
        
        logger.info(f"User {user_id} has {count} unread notifications")
        return count

    def get_unread_notifications(self, user_id: str, language_code: str = "vi") -> List[dict]:
        """Get only unread notifications for a user"""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).order_by(Notification.created_at.desc()).all()
        
        results = []
        for n in notifications:
            trans = self._get_notification_translation(n.id, language_code)
            
            results.append({
                "id": n.id,
                "user_id": n.user_id,
                "type": n.type,
                "title": trans.title if trans else n.title,
                "message": trans.message if trans else n.message,
                "is_read": n.is_read,
                "related_entity_id": n.related_entity_id,
                "created_at": n.created_at,
                "language_code": language_code,
            })
        
        logger.info(f"Retrieved {len(results)} unread notifications for user {user_id}")
        return results
