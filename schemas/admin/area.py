from pydantic import BaseModel
from typing import Optional

class AreaBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    center_lat: float
    center_long: float
    radius: Optional[int] = 500

class AreaCreate(AreaBase):
    pass

class AreaUpdate(AreaBase):
    pass

class Area(AreaBase):
    id: str

    class Config:
        from_attributes = True
