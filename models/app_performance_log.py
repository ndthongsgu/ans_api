import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Text, Index, ForeignKey
)
from core.database import Base

class AppPerformanceLog(Base):
    __tablename__ = "app_performance_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    device_model = Column(String(100), default=None)
    os_version = Column(String(50), default=None)
    app_version = Column(String(20), default=None)
    event_name = Column(String(100), nullable=False)
    event_duration_ms = Column(Integer, default=None)
    memory_usage_mb = Column(Float, default=None)
    battery_usage_percent = Column(Float, default=None)
    network_type = Column(String(20), default=None)
    timestamp = Column(Integer, nullable=False)
    details = Column(Text, default=None)