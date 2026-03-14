from pydantic import BaseModel
from typing import List, Optional

class StallContentPageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    title: Optional[str] = None
    stall_id: Optional[str] = None
    is_active: Optional[bool] = None

class StallContentCreate(BaseModel):
    stall_id: str
    language_code: Optional[str] = "vi"
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    audio_url: str
    audio_duration: Optional[int] = None
    audio_file_size: Optional[int] = None
    tts_script: Optional[str] = None
    version: Optional[int] = 1

class StallContentUpdate(BaseModel):
    stall_id: str
    language_code: Optional[str] = "vi"
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    audio_url: str
    audio_duration: Optional[int] = None
    audio_file_size: Optional[int] = None
    tts_script: Optional[str] = None
    version: Optional[int] = 1

class StallContentOut(BaseModel):
    id: str
    stall_id: str
    language_code: str
    title: str
    description: Optional[str]
    short_description: Optional[str]
    audio_url: str
    audio_duration: Optional[int]
    audio_file_size: Optional[int]
    tts_script: Optional[str]
    version: int
    is_active: bool