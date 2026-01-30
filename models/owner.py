import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship, declarative_base
from core.database import Base

class Owner(Base):
    __tablename__ = "owners"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    subscription_package_id = Column(String(36), ForeignKey("subscription_packages.id"), nullable=True)
    subscription_expires_at = Column(Integer, nullable=True)
    business_name = Column(String(255), nullable=True)
    business_address = Column(Text, nullable=True)

    user = relationship("User", back_populates="owner")
    subscription_package = relationship("SubscriptionPackage", back_populates="owners")

    stalls = relationship(
        "Stall",
        back_populates="owner",
        cascade="all, delete-orphan"
    )