from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class StallContentTranslation(BaseModel):
    __tablename__ = "stall_content_translations"

    stall_content_id = Column(String(36), ForeignKey("stall_contents.id"), nullable=False)
    language_code = Column(String(10), default="vi", nullable=False)
    audio_url = Column(String(500), nullable=False)
    audio_duration = Column(Integer)
    audio_file_size = Column(Integer)
    tts_script = Column(Text, nullable=True)

    stall_content = relationship("StallContent", back_populates="translations")

    __table_args__ = (
        Index("idx_stall_content_language", "stall_content_id", "language_code"),
    )
