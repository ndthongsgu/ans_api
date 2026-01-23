from pydantic import BaseModel
from typing import Optional

class StallContentBase(BaseModel):
    stall_id: str
    language_code: Optional[str] = "vi"
    title: str
    description: Optional[str] = None
    audio_url: str

class StallContentCreate(StallContentBase):
    pass

class StallContentUpdate(StallContentBase):
    pass

class StallContent(StallContentBase):
    id: str

    class Config:
        from_attributes = True
