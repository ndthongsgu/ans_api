from sqlalchemy import (
    Column, String, Integer, Text, Boolean, Index, ForeignKey
)
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="system")
    data = Column(JSON, default=None)
    is_read = Column(Boolean, default=False)
    sent_at = Column(Integer, nullable=False)
    read_at = Column(Integer, nullable=True)

    translations = relationship(
        "NotificationTranslation",
        back_populates="notification",
        cascade="all, delete-orphan"
    )