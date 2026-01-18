import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from core.database import Base


class ListeningHistory(Base):
    __tablename__ = "listening_histories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    stall_id = Column(String(36), ForeignKey("stalls.id"), nullable=False)
    stall_content_id = Column(String(36), ForeignKey("stall_contents.id"), nullable=False)

    listened_at = Column(Integer, nullable=False)
    listen_duration = Column(Integer)

    user = relationship("User", back_populates="listening_histories")
    stall = relationship("Stall")
    content = relationship("StallContent", back_populates="listening_histories")
