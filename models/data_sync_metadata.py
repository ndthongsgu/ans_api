from sqlalchemy import (
    Column, String, Integer, Index
)
from models.base import BaseModel

class DataSyncMetadata(BaseModel):
    __tablename__ = "data_sync_metadata"

    table_name = Column(String(50), nullable=False)
    last_sync_version = Column(String(64), nullable=False)
    last_updated_at = Column(Integer, nullable=False)
    record_count = Column(Integer, default=0)
    checksum = Column(String(64), default=None)
    sync_interval = Column(Integer, default=3600)