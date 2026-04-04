from sqlalchemy import (
    Column, String, Integer, Boolean, Text,
    ForeignKey
)
from sqlalchemy.orm import relationship
from models.base import BaseModel

class Owner(BaseModel):
    __tablename__ = "owners"
    user_id = Column(String(36), ForeignKey("users.id"), unique=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    subscription_expires_at = Column(Integer, nullable=True)
    business_name = Column(String(255), nullable=True)
    business_address = Column(Text, nullable=True)
    subscription_package_id = Column(String(36), ForeignKey("subscription_packages.id"), nullable=True)

    user = relationship("User", back_populates="owner")
    subscription_package = relationship("SubscriptionPackage", back_populates="owners")
    subscription_transactions = relationship(
        "SubscriptionTransaction",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    stalls = relationship(
        "Stall",
        back_populates="owner",
        cascade="all, delete-orphan"
    )