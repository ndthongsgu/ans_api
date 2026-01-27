from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    user_id: Optional[str] = None
    full_name: str
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: str

    class Config:
        from_attributes = True
