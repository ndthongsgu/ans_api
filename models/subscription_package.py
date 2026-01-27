import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
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
    max_stalls = Column(Integer, nullable=False)  # maximum number of stalls the owner can create
    features = Column(Text, nullable=True)  # JSON string or text

    owners = relationship("Owner", back_populates="subscription_package")
