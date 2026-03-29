from pydantic import BaseModel
from typing import Optional, List


class SubscriptionPackagePageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    name: Optional[str] = None
    code: Optional[str] = None


class SubscriptionPackageCreate(BaseModel):
    name: str
    code: str
    price: float
    max_stalls: int
    description: Optional[str] = None


class SubscriptionPackageUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    price: Optional[float] = None
    max_stalls: Optional[int] = None
    description: Optional[str] = None


class SubscriptionPackageOut(BaseModel):
    id: str
    name: str
    code: str
    price: float
    max_stalls: int
    description: Optional[str] = None
    created_at: int
    updated_at: Optional[int] = None

