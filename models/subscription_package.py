from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel

class SubscriptionPackage(BaseModel):
    __tablename__ = "subscription_packages"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)  # in days
    max_stalls = Column(Integer, default=1, nullable=False)  # maximum number of stalls the owner can create
    max_audio_storage = Column(Integer, default=100)
    features = Column(Text, nullable=True)  # JSON string or text

    owners = relationship("Owner", back_populates="subscription_package")
