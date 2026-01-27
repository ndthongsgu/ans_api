from pydantic import BaseModel
from typing import Optional

class OwnerBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    user_id: Optional[str] = None
    subscription_package_id: Optional[str] = None

class OwnerCreate(OwnerBase):
    pass

class OwnerUpdate(OwnerBase):
    pass

class Owner(OwnerBase):
    id: str

    class Config:
        from_attributes = True
