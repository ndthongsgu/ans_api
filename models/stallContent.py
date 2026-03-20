from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class StallContent(BaseModel):
    __tablename__ = "stall_contents"

    stall_id = Column(String(36), ForeignKey("stalls.id"), nullable=False)

    language_code = Column(String(10), default="vi")
    title = Column(String(255), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    audio_url = Column(String(500), nullable=False)
    audio_duration = Column(Integer)
    audio_file_size = Column(Integer)
    tts_script = Column(Text)
    version = Column(Integer, default=1)

    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)

    stall = relationship("Stall", back_populates="contents")
    listening_histories = relationship(
        "ListeningHistory",
        back_populates="content"
    )
