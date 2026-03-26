from sqlalchemy import (
    Column, String, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class StallTranslation(BaseModel):
    __tablename__ = "stall_translations"

    stall_id = Column(String(36), ForeignKey("stalls.id"), nullable=False)
    language_code = Column(String(10), default="vi", nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)

    stall = relationship("Stall", back_populates="translations")

    __table_args__ = (
        Index("idx_stall_language", "stall_id", "language_code"),
    )
