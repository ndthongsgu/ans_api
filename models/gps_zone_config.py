from sqlalchemy import (
    Column, String, Integer, Boolean, Index
)
from models.base import BaseModel

class GPSZoneConfig(BaseModel):
    __tablename__ = "gps_zone_configs"

    zone_name = Column(String(50), nullable=False)
    min_distance = Column(Integer, nullable=False)
    max_distance = Column(Integer, nullable=False)
    polling_interval = Column(Integer, nullable=False)
    gps_accuracy = Column(String(20), default="balanced")
    battery_saving = Column(Boolean, default=True)