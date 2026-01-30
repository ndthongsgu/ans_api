import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    username = Column(String(100), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)

    preferred_language = Column(String(10), default="vi")
    is_active = Column(Boolean, default=True)

    created_at = Column(Integer, nullable=False)
    last_sync_at = Column(Integer, nullable=True)
    device_id = Column(String(255), nullable=True)
    notification_token = Column(String(255), nullable=True)

    roles = relationship("UserRole", back_populates="user")
    listening_histories = relationship(
        "ListeningHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    customer = relationship("Customer", uselist=False, back_populates="user")
    employee = relationship("Employee", uselist=False, back_populates="user")
    owner = relationship("Owner", uselist=False, back_populates="user")
