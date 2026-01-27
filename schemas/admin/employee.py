from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    user_id: Optional[str] = None
    full_name: str
    phone: Optional[str] = None
    position: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: str

    class Config:
        from_attributes = True
