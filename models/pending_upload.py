from sqlalchemy import (
    Column, String, Integer, Text, Index, ForeignKey
)
from sqlalchemy import JSON
from models.base import BaseModel

class PendingUpload(BaseModel):
    __tablename__ = "pending_uploads"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(20), default="pending")
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, default=None)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)
    synced_at = Column(Integer, nullable=True)