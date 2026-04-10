from sqlalchemy import Column, String, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.base import BaseModel


class SubscriptionTransaction(BaseModel):
    __tablename__ = "subscription_transactions"

    owner_id = Column(String(36), ForeignKey("owners.id"), nullable=False)
    subscription_package_id = Column(String(36), ForeignKey("subscription_packages.id"), nullable=False)

    transaction_code = Column(String(50), nullable=False, unique=True)
    order_id = Column(String(100), nullable=False, unique=True)
    request_id = Column(String(100), nullable=False, unique=True)

    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="VND")
    payment_method = Column(String(50), nullable=False, default="vnpay")
    payment_provider = Column(String(50), nullable=False, default="vnpay")
    payment_status = Column(String(20), nullable=False, default="pending")

    payment_url = Column(Text, nullable=True)
    qr_code_url = Column(Text, nullable=True)
    vnpay_trans_id = Column(String(100), nullable=True)
    vnpay_response_code = Column(String(20), nullable=True)
    vnpay_raw_response = Column(Text, nullable=True)

    paid_at = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    raw_payload = Column(Text, nullable=True)

    owner = relationship("Owner", back_populates="subscription_transactions")
    package = relationship("SubscriptionPackage", back_populates="transactions")
