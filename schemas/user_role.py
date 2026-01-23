from pydantic import BaseModel

class UserRoleBase(BaseModel):
    user_id: str
    role_id: str

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(UserRoleBase):
    pass

class UserRole(UserRoleBase):
    id: str

    class Config:
        from_attributes = True
