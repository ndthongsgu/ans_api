from pydantic import BaseModel, EmailStr
from typing import List, Optional

class CustomerPageRequest(BaseModel):
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
    customerTypeId: Optional[str] = None

class CustomerCreate(BaseModel):
    # code: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    # description: Optional[str] = None
    password: str
    customerTypeId: Optional[str] = None

class CustomerUpdate(BaseModel):
    # code: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    # description: Optional[str] = None
    customerTypeId: Optional[str] = None

class CustomerOut(BaseModel):
    id: str
    code: str
    name: str
    email: EmailStr
    phone: Optional[str]
    description: Optional[str]
    is_active: bool