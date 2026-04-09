from pydantic import BaseModel, Field


class StallContentCreateRequest(BaseModel):
    stall_id: str = Field(min_length=1)
    tts_script: str = Field(min_length=1, max_length=5000)


class StallContentUpdateRequest(BaseModel):
    stall_id: str | None = Field(default=None, min_length=1)
    tts_script: str | None = Field(default=None, max_length=5000)


class StallContentResponse(BaseModel):
    id: str
    stall_id: str
    stall_name: str | None = None
    tts_script: str | None = None
    created_at: int
    updated_at: int | None = None
    is_deleted: bool


class StallContentListResponse(BaseModel):
    data: list[StallContentResponse]
    total: int


class StallWithoutContentResponse(BaseModel):
    stall_id: str
    stall_name: str


class StallWithoutContentListResponse(BaseModel):
    data: list[StallWithoutContentResponse]
    total: int
