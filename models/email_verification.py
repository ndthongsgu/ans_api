import uuid
import time
from sqlalchemy import Column, String, Integer, Boolean
from core.database import Base


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    email = Column(String(255), index=True, nullable=False)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)

    otp_code = Column(String(10), nullable=False)
    expires_at = Column(Integer, nullable=False)
    verified = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
