import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from core.database import Base

class SubscriptionPackage(Base):
    __tablename__ = "subscription_packages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)  # in days
    max_stalls = Column(Integer, default=1, nullable=False)  # maximum number of stalls the owner can create
    max_audio_storage = Column(Integer, default=100)
    features = Column(Text, nullable=True)  # JSON string or text
    is_active = Column(Boolean, default=True)

    owners = relationship("Owner", back_populates="subscription_package")
