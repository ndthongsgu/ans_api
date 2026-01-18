import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship, declarative_base
from core.database import Base

class Staff(Base):
    __tablename__ = "staffs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    user = relationship("User", back_populates="staff")

    stalls = relationship(
        "Stall",
        back_populates="staff",
        cascade="all, delete-orphan"
    )