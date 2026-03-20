from sqlalchemy import (
    Column, String, Text, Boolean
)
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"

    code = Column(String(50), unique=True, nullable=False)  # ADMIN, STAFF, OWNER, USER
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    permissions = Column(Text, nullable=True)  # JSON or comma-separated permissions

    users = relationship("UserRole", back_populates="role")
