from sqlalchemy import (Column, String, Integer, Text, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class StallContent(BaseModel):
    __tablename__ = "stall_contents"
    __table_args__ = (
        UniqueConstraint("stall_id", name="uq_stall_contents_stall_id"),
    )

    stall_id = Column(String(36), ForeignKey("stalls.id"), nullable=False)

    tts_script = Column(Text)
    stall = relationship("Stall", back_populates="contents")
    listening_histories = relationship(
        "ListeningHistory",
        back_populates="content"
    )
    translations = relationship(
        "StallContentTranslation",
        back_populates="stall_content",
        cascade="all, delete-orphan"
    )
