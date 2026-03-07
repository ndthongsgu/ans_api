from pydantic import BaseModel, EmailStr
from typing import List, Optional

class OwnerPageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    isDeleted: Optional[bool] = None

class OwnerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    subscription_package_id: Optional[str] = None

class OwnerUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    business_name: Optional[str] = None
    business_address: Optional[str] = None
    subscription_package_id: Optional[str] = None

class OwnerOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str]
    business_name: Optional[str]
    business_address: Optional[str]
    is_active: bool