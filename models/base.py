

import uuid
from sqlalchemy import Boolean, Column, Integer, String
from core.database import Base


class BaseModel(Base):
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    is_deleted = Column(Boolean, default=False)
    version = Column(Integer, default=1)
