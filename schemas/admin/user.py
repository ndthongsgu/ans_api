from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: str
    is_active: bool
    created_at: int

    class Config:
        from_attributes = True
