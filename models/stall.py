import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from core.database import Base


class Stall(Base):
    __tablename__ = "stalls"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    area_id = Column(String(36), ForeignKey("areas.id"), nullable=False)
    owner_id = Column(String(36), ForeignKey("owners.id"), nullable=False)

    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    radius = Column(Integer, default=15)
    cover_image = Column(String(500))
    status = Column(Boolean, default=True)

    area = relationship("Area", back_populates="stalls")
    owner = relationship("Owner", back_populates="stalls")
    contents = relationship(
        "StallContent",
        back_populates="stall",
        cascade="all, delete-orphan"
    )
