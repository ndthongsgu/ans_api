from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric, Index
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Stall(BaseModel):
    __tablename__ = "stalls"

    owner_id = Column(String(36), ForeignKey("owners.id"), nullable=False)

    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Integer, default=50)
    cover_image = Column(Text)
    category = Column(String(100))
    price_range = Column(String(20))
    opening_hours = Column(Text)
    close_hours = Column(Text)
    contact_phone = Column(String(20))
    website = Column(String(255))
    average_rating = Column(Numeric(3, 2), default=0.00)
    total_reviews = Column(Integer, default=0)

    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)

    owner = relationship("Owner", back_populates="stalls")
    contents = relationship(
        "StallContent",
        back_populates="stall",
        cascade="all, delete-orphan"
    )
    translations = relationship(
        "StallTranslation",
        back_populates="stall",
        cascade="all, delete-orphan"
    )
