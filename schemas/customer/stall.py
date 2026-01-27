from pydantic import BaseModel
from typing import Optional

class StallBase(BaseModel):
    area_id: str
    owner_id: str
    name: str
    latitude: float
    longitude: float
    radius: Optional[int] = 15
    cover_image: Optional[str] = None
    status: Optional[bool] = True

class StallCreate(StallBase):
    pass

class StallUpdate(StallBase):
    pass

class Stall(StallBase):
    id: str

    class Config:
        from_attributes = True
