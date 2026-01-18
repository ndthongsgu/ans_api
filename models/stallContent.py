import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from core.database import Base


class StallContent(Base):
    __tablename__ = "stall_contents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stall_id = Column(String(36), ForeignKey("stalls.id"), nullable=False)

    language_code = Column(String(10), default="vi")
    title = Column(String(255), nullable=False)
    description = Column(Text)
    audio_url = Column(String(500), nullable=False)

    stall = relationship("Stall", back_populates="contents")
    listening_histories = relationship(
        "ListeningHistory",
        back_populates="content"
    )
