from sqlalchemy import (
    Column, String, Text, Boolean,
    ForeignKey
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Employee(BaseModel):
    __tablename__ = "employees"
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    code = Column(String(50), unique=True, nullable=False)

    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    user = relationship("User", back_populates="employee")
