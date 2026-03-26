from sqlalchemy import (
    Column, String, Boolean, Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Customer(BaseModel):
    __tablename__ = "customers"

    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    notification_enabled = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)
    subscription_expires_at = Column(Integer, nullable=True)

    user = relationship("User", back_populates="customer")

    # Relationships
    # listening_histories = relationship(
    #     "ListeningHistory",
    #     back_populates="customer",
    #     cascade="all, delete-orphan"
    # )
