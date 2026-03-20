from sqlalchemy import (
    Column, String, Integer, Boolean, Index, ForeignKey
)
from models.base import BaseModel

class AudioPlaybackRule(BaseModel):
    __tablename__ = "audio_playback_rules"

    stall_id = Column(String(36), ForeignKey("stalls.id"), nullable=False)
    priority = Column(Integer, default=0)
    cooldown_seconds = Column(Integer, default=900)
    debounce_seconds = Column(Integer, default=3)
    pre_fetch_audio = Column(Boolean, default=True)
    use_tts_as_fallback = Column(Boolean, default=True)
    fade_in_duration = Column(Integer, default=1000)
    fade_out_duration = Column(Integer, default=1000)
    min_listen_duration = Column(Integer, default=5000)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=True)