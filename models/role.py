import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from core.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False)  # ADMIN, STAFF, OWNER, USER
    name = Column(String(100), nullable=False)

    permissions = Column(Text, nullable=True)  # JSON or comma-separated permissions

    users = relationship("UserRole", back_populates="role")
