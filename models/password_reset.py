import time
import uuid
from sqlalchemy import Column, String, Integer, Boolean
from models.base import BaseModel


class PasswordReset(BaseModel):
    __tablename__ = "password_resets"

    email = Column(String(255), index=True, nullable=False)
    otp_code = Column(String(10), nullable=False)
    expires_at = Column(Integer, nullable=False)
    used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(Integer, nullable=False, default=lambda: int(time.time()))
