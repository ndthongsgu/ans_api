from pydantic import BaseModel
from typing import List, Optional

class SubscriptionPackagePageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    name: Optional[str] = None
    is_deleted: Optional[bool] = None

class SubscriptionPackageCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration: int
    max_stalls: Optional[int] = 1
    max_audio_storage: Optional[int] = 100
    features: Optional[str] = None

class SubscriptionPackageUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration: int
    max_stalls: Optional[int] = 1
    max_audio_storage: Optional[int] = 100
    features: Optional[str] = None

class SubscriptionPackageOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: float
    duration: int
    max_stalls: int
    max_audio_storage: int
    features: Optional[str]
    is_deleted: bool