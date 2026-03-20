from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel

class CustomerSubscriptionPackage(BaseModel):
    __tablename__ = "customer_subscription_packages"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    duration = Column(Integer, nullable=False)  # in days or hours? assuming days for consistency
    features = Column(Text, nullable=True)  # JSON string or text

    customers = relationship("Customer", back_populates="subscription_package")
