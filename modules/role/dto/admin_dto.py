from pydantic import BaseModel
from typing import List, Optional

class RolePageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    code: Optional[str] = None
    name: Optional[str] = None

class RoleCreate(BaseModel):
    code: str
    name: str
    permissions: Optional[str] = None

class RoleUpdate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    permissions: Optional[str] = None

class RoleOut(BaseModel):
    id: str
    code: str
    name: str
    permissions: Optional[str]