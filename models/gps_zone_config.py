import uuid
from sqlalchemy import (
    Column, String, Integer, Boolean, Index
)
from core.database import Base

class GPSZoneConfig(Base):
    __tablename__ = "gps_zone_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zone_name = Column(String(50), nullable=False)
    min_distance = Column(Integer, nullable=False)
    max_distance = Column(Integer, nullable=False)
    polling_interval = Column(Integer, nullable=False)
    gps_accuracy = Column(String(20), default="balanced")
    battery_saving = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)