import uuid
from sqlalchemy import (
    Column, String, Integer, Text, Index, ForeignKey
)
from sqlalchemy import JSON
from core.database import Base

class PendingUpload(Base):
    __tablename__ = "pending_uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(20), default="pending")
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, default=None)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)
    synced_at = Column(Integer, nullable=True)