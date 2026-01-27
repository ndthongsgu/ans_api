from pydantic import BaseModel
from typing import Optional

class RoleBase(BaseModel):
    code: str
    name: str
    permissions: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class Role(RoleBase):
    id: str

    class Config:
        from_attributes = True
