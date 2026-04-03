from pydantic import BaseModel, Field


class ListeningHistoryCreateRequest(BaseModel):
    stall_id: str = Field(..., description="ID of the stall")
    stall_content_id: str = Field(..., description="ID of the stall content (audio)")
    listened_at: int = Field(..., description="Timestamp in seconds since epoch")
    listen_duration: int | None = Field(None, description="Listen duration in seconds")
