from pydantic import BaseModel
from typing import Optional

# Subscription-related DTOs

class PackageOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    duration: int
    features: Optional[str] = None

class SubscriptionOut(BaseModel):
    package_id: Optional[str] = None
    package_name: Optional[str] = None
    expires_at: Optional[int] = None
    active: bool = False
