from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class SubscriptionPackageBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    duration: int
    max_stalls: int
    features: Optional[str] = None

class SubscriptionPackageCreate(SubscriptionPackageBase):
    pass

class SubscriptionPackageUpdate(SubscriptionPackageBase):
    pass

class SubscriptionPackage(SubscriptionPackageBase):
    id: str

    class Config:
        from_attributes = True
