from pydantic import BaseModel


class StallContentCreateRequest(BaseModel):
	stall_id: str
	language_code: str | None = "vi"
	tts_script: str


class StallContentUpdateRequest(BaseModel):
	language_code: str | None = None
	tts_script: str | None = None


class ToggleContentRequest(BaseModel):
	is_deleted: str | bool


class StallContentResponse(BaseModel):
	id: str
	stall_id: str
	stall_name: str | None = None
	language_code: str
	title: str | None = None
	description: str | None = None
	audio_url: str | None = None
	audio_duration: int | None = None
	audio_file_size: int | None = None
	tts_script: str | None = None
	version: int
	is_deleted: bool
	created_at: int
	updated_at: int | None = None


class StallWithoutContentResponse(BaseModel):
	stall_id: str
	stall_name: str