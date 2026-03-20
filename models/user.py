from sqlalchemy import (
    Column, String, Integer, Boolean, Text,
    ForeignKey
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)

    preferred_language = Column(String(10), default="vi")

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

    is_admin = Column(Boolean, default=False)

    customer = relationship("Customer", uselist=False, back_populates="user")
    employee = relationship("Employee", uselist=False, back_populates="user")
    owner = relationship("Owner", uselist=False, back_populates="user")
    action_logs = relationship("ActionLog", back_populates="user")
