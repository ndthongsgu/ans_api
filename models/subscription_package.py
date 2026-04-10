from sqlalchemy import Column, String, Integer, Numeric, Text
from sqlalchemy.orm import relationship
from models.base import BaseModel


class SubscriptionPackage(BaseModel):
    __tablename__ = "subscription_packages"

    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    price = Column(Numeric(12, 2), nullable=False, default=0.00)
    max_stalls = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)

    owners = relationship("Owner", back_populates="subscription_package")
    transactions = relationship("SubscriptionTransaction", back_populates="package")
