from pydantic import BaseModel
from typing import List, Optional

class StallContentPageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    stall_id: Optional[str] = None
    is_deleted: Optional[bool] = None

class StallContentCreate(BaseModel):
    stall_id: str
    language_code: Optional[str] = "vi"
    audio_url: Optional[str] = None  # Optional if tts_script is provided
    audio_duration: Optional[int] = None
    audio_file_size: Optional[int] = None
    tts_script: Optional[str] = None  # TTS script for auto audio generation
    version: Optional[int] = 1

class StallContentUpdate(BaseModel):
    stall_id: str
    language_code: Optional[str] = "vi"
    audio_url: Optional[str] = None  # Optional if tts_script is provided
    audio_duration: Optional[int] = None
    audio_file_size: Optional[int] = None
    tts_script: Optional[str] = None  # TTS script for auto audio generation
    version: Optional[int] = 1

class StallContentOut(BaseModel):
    id: str
    stall_id: str
    language_code: str
    audio_url: str
    audio_duration: Optional[int]
    audio_file_size: Optional[int]
    tts_script: Optional[str]
    version: int
    is_deleted: bool