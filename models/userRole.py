import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from core.database import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    code = Column(String(50), nullable=False)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
