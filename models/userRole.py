from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel

class UserRole(BaseModel):
    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    code = Column(String(50), nullable=False)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
