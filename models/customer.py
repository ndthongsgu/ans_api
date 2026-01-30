import uuid
from sqlalchemy import (
    Column, String, Boolean, Integer,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship, declarative_base
from core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    notification_enabled = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="customer")

    # Relationships
    listening_histories = relationship(
        "ListeningHistory",
        back_populates="customer",
        cascade="all, delete-orphan"
    )
