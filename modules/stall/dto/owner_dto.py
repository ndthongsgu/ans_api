from pydantic import BaseModel, Field, model_validator


class OpeningHourItem(BaseModel):
	day_of_week: int = Field(ge=0, le=6)
	open_time: str | None = None
	close_time: str | None = None
	closed: bool = False

	@model_validator(mode="after")
	def validate_time_range(self):
		if not self.closed and (not self.open_time or not self.close_time):
			raise ValueError("open_time and close_time are required when closed is false")
		return self


class CreateStallRequest(BaseModel):
	name: str = Field(min_length=1, max_length=255)
	latitude: float = Field(ge=-90, le=90)
	longitude: float = Field(ge=-180, le=180)
	radius: int = Field(default=50, ge=1)
	cover_image: str | None = None
	opening_hours: list[OpeningHourItem] | str | None = None
	close_hours: str | None = Field(default=None, max_length=100)
	category: str | None = Field(default=None, max_length=100)
	price_range: str | int | None = None
	contact_phone: str | None = Field(default=None, max_length=20)
	website: str | None = Field(default=None, max_length=255)


class UpdateStallRequest(BaseModel):
	name: str | None = Field(default=None, min_length=1, max_length=255)
	latitude: float | None = Field(default=None, ge=-90, le=90)
	longitude: float | None = Field(default=None, ge=-180, le=180)
	radius: int | None = Field(default=None, ge=1)
	cover_image: str | None = None
	opening_hours: list[OpeningHourItem] | str | None = None
	close_hours: str | None = Field(default=None, max_length=100)
	category: str | None = Field(default=None, max_length=100)
	price_range: str | int | None = None
	contact_phone: str | None = Field(default=None, max_length=20)
	website: str | None = Field(default=None, max_length=255)


class StallResponse(BaseModel):
	id: str
	owner_id: str
	name: str
	latitude: float
	longitude: float
	radius: int
	cover_image: str | None = None
	contact_phone: str | None = None
	website: str | None = None
	opening_hours: list[OpeningHourItem] | str | None = None
	close_hours: str | None = None
	category: str | None = None
	price_range: str | int | None = None
	average_rating: float
	total_reviews: int
	created_at: int
	updated_at: int | None = None


class CreateStallContentRequest(BaseModel):
	language_code: str = Field(default="vi", min_length=2, max_length=10)
	title: str = Field(min_length=1, max_length=255)
	description: str | None = None
	short_description: str | None = Field(default=None, max_length=500)
	audio_url: str = Field(min_length=1, max_length=500)
	audio_duration: int | None = Field(default=None, ge=0)
	audio_file_size: int | None = Field(default=None, ge=0)
	tts_script: str | None = None
	version: int = Field(default=1, ge=1)
	is_active: bool = True
	auto_translate: bool = False
	target_languages: list[str] | None = None


class UpdateStallContentRequest(BaseModel):
	language_code: str | None = Field(default=None, min_length=2, max_length=10)
	title: str | None = Field(default=None, min_length=1, max_length=255)
	description: str | None = None
	short_description: str | None = Field(default=None, max_length=500)
	audio_url: str | None = Field(default=None, min_length=1, max_length=500)
	audio_duration: int | None = Field(default=None, ge=0)
	audio_file_size: int | None = Field(default=None, ge=0)
	tts_script: str | None = None
	version: int | None = Field(default=None, ge=1)
	is_active: bool | None = None
	auto_translate: bool | None = None
	target_languages: list[str] | None = None


class StallContentResponse(BaseModel):
	id: str
	stall_id: str
	language_code: str
	title: str
	description: str | None = None
	short_description: str | None = None
	audio_url: str
	audio_duration: int | None = None
	audio_file_size: int | None = None
	tts_script: str | None = None
	version: int
	is_active: bool
	created_at: int
	updated_at: int | None = None
