from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.base import BaseModel


class SubscriptionTransaction(BaseModel):
    __tablename__ = "subscription_transactions"

    owner_id = Column(String(36), ForeignKey("owners.id"), nullable=False)
    package_id = Column(String(36), ForeignKey("subscription_packages.id"), nullable=False)

    transaction_code = Column(String(50), nullable=False, unique=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), nullable=False, default="VND")
    payment_method = Column(String(50), nullable=True)
    payment_provider = Column(String(50), nullable=True)
    payment_reference = Column(String(100), nullable=True)
    payment_status = Column(String(20), nullable=False, default="completed")
    subscription_start_at = Column(Integer, nullable=False)
    subscription_end_at = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    raw_payload = Column(Text, nullable=True)

    owner = relationship("Owner", back_populates="subscription_transactions")
    package = relationship("SubscriptionPackage", back_populates="transactions")
