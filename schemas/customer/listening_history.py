from pydantic import BaseModel
from typing import Optional

class ListeningHistoryBase(BaseModel):
    user_id: Optional[str] = None
    stall_id: str
    stall_content_id: str
    listened_at: int
    listen_duration: Optional[int] = None

class ListeningHistoryCreate(ListeningHistoryBase):
    pass

class ListeningHistoryUpdate(ListeningHistoryBase):
    pass

class ListeningHistory(ListeningHistoryBase):
    id: str

    class Config:
        from_attributes = True
