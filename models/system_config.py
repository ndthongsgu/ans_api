from sqlalchemy import (
    Column, String, Integer, Text, Boolean, Index
)
from models.base import BaseModel

class SystemConfig(BaseModel):
    __tablename__ = "system_configs"

    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, default=None)
    config_type = Column(String(20), default="string")
    category = Column(String(50), default="general")
    description = Column(Text, default=None)
    is_public = Column(Boolean, default=False)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)