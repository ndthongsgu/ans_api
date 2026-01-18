import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from core.database import Base

class Area(Base):
    __tablename__ = "areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))

    center_lat = Column(Float, nullable=False)
    center_long = Column(Float, nullable=False)
    radius = Column(Integer, default=500)

    stalls = relationship(
        "Stall",
        back_populates="area",
        cascade="all, delete-orphan"
    )
