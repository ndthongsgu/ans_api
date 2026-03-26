from pydantic import BaseModel, Field


class OwnerStallContentCreateRequest(BaseModel):
    stallId: str = Field(min_length=1)
    languageCode: str = Field(default="vi", min_length=2, max_length=10)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    shortDescription: str | None = Field(default=None, max_length=500)
    audioUrl: str = Field(min_length=1, max_length=500)
    audioDuration: int | None = Field(default=None, ge=0)
    audioFileSize: int | None = Field(default=None, ge=0)
    ttsScript: str | None = None
    version: int = Field(default=1, ge=1)
    isActive: bool = True
    autoTranslate: bool = False
    targetLanguages: list[str] | None = None


class OwnerStallContentResponse(BaseModel):
    id: str
    stallId: str
    languageCode: str
    title: str
    description: str | None = None
    shortDescription: str | None = None
    audioUrl: str
    audioDuration: int | None = None
    audioFileSize: int | None = None
    ttsScript: str | None = None
    version: int
    isActive: bool
    createdAt: int
    updatedAt: int | None = None
