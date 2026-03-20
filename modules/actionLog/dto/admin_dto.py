from pydantic import BaseModel
from typing import Optional


class ActionLogCreate(BaseModel):
    function_type: str
    function_id: str
    action: str
    change_details: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ActionLogOut(BaseModel):
    id: str
    function_type: str
    function_id: str
    action: str
    change_details: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    created_at: int
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None


class ActionLogPageRequest(BaseModel):
    page: int = 0
    size: int = 10
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = None
    functionType: Optional[str] = None
    functionId: Optional[str] = None
    type: Optional[str] = None
    createdBy: Optional[str] = None
