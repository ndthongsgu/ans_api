from pydantic import BaseModel
from typing import List, Optional

class StallPageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    name: Optional[str] = None
    owner_id: Optional[str] = None
    category: Optional[str] = None

class StallCreate(BaseModel):
    owner_id: str
    name: str
    latitude: float
    longitude: float
    radius: Optional[int] = 50
    cover_image: Optional[str] = None
    category: Optional[str] = None
    price_range: Optional[str] = None
    opening_hours: Optional[str] = None
    close_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None

class StallUpdate(BaseModel):
    owner_id: Optional[str] = None
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[int] = None
    cover_image: Optional[str] = None
    category: Optional[str] = None
    price_range: Optional[str] = None
    opening_hours: Optional[str] = None
    close_hours: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None

class StallOut(BaseModel):
    id: str
    owner_id: str
    name: str
    latitude: float
    longitude: float
    radius: int
    cover_image: Optional[str]
    category: Optional[str]
    price_range: Optional[str]
    opening_hours: Optional[str]
    close_hours: Optional[str]
    contact_phone: Optional[str]
    website: Optional[str]
    average_rating: float
    total_reviews: int
