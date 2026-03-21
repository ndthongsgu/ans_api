from sqlalchemy import (
    Column, String, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class NotificationTranslation(BaseModel):
    __tablename__ = "notification_translations"

    notification_id = Column(String(36), ForeignKey("notifications.id"), nullable=False)
    language_code = Column(String(10), default="vi", nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    notification = relationship("Notification", back_populates="translations")

    __table_args__ = (
        Index("idx_notification_language", "notification_id", "language_code"),
    )
