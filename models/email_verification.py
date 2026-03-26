import uuid
from sqlalchemy import Column, String, Integer, Boolean
from models.base import BaseModel


class EmailVerification(BaseModel):
    __tablename__ = "email_verifications"

    email = Column(String(255), index=True, nullable=False)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)

    otp_code = Column(String(10), nullable=False)
    expires_at = Column(Integer, nullable=False)
    verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
