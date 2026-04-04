from pydantic import BaseModel, Field, field_validator

from common.enums.language import LanguageCode


class StallContentCreateRequest(BaseModel):
    stall_id: str = Field(min_length=1)
    language_code: str = Field(default=LanguageCode.DEFAULT, min_length=2, max_length=10)
    tts_script: str = Field(min_length=1, max_length=5000)

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in LanguageCode.get_codes():
            raise ValueError("invalid_language_code")
        return normalized


class StallContentUpdateRequest(BaseModel):
    language_code: str | None = Field(default=None, min_length=2, max_length=10)
    tts_script: str | None = Field(default=None, max_length=5000)

    @field_validator("language_code")
    @classmethod
    def validate_language_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in LanguageCode.get_codes():
            raise ValueError("invalid_language_code")
        return normalized


class StallContentResponse(BaseModel):
    id: str
    stall_id: str
    stall_name: str | None = None
    language_code: str
    audio_url: str
    audio_duration: int | None = None
    audio_file_size: int | None = None
    tts_script: str | None = None
    is_deleted: bool
    created_at: int
    updated_at: int | None = None


class StallContentListResponse(BaseModel):
    data: list[StallContentResponse]
    total: int


class StallWithoutContentResponse(BaseModel):
    stall_id: str
    stall_name: str


class StallWithoutContentListResponse(BaseModel):
    data: list[StallWithoutContentResponse]
    total: int
