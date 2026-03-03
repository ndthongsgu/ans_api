from pydantic import BaseModel, EmailStr
from typing import List, Optional

class EmployeePageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    code: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    isDeleted: Optional[bool] = None
    roleIds: Optional[List[str]] = None
    roleFilterMode: Optional[str] = None  # OR, AND, EXCLUDE

class EmployeeCreate(BaseModel):
    code: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    description: Optional[str] = None
    roles: List[str]
    password: str

class EmployeeUpdate(BaseModel):
    code: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    description: Optional[str] = None
    roles: List[str]

class EmployeeOut(BaseModel):
    id: str
    code: str
    name: str
    email: EmailStr
    phone: Optional[str]
    description: Optional[str]
    is_active: bool
    roles: List[str]
