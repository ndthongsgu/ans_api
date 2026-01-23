from pydantic import BaseModel
from typing import Optional

class StaffBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    user_id: Optional[str] = None

class StaffCreate(StaffBase):
    pass

class StaffUpdate(StaffBase):
    pass

class Staff(StaffBase):
    id: str

    class Config:
        from_attributes = True
