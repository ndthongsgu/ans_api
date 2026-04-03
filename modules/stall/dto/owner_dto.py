from pydantic import BaseModel, Field, model_validator, field_validator


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

	@field_validator("cover_image", mode="before")
	@classmethod
	def normalize_cover_image(cls, value):
		if value is None:
			return None

		if isinstance(value, str):
			return value

		if isinstance(value, dict):
			if not value:
				return None

			for key in ("data_url", "url", "value", "base64"):
				candidate = value.get(key)
				if isinstance(candidate, str):
					if key == "base64":
						mime = value.get("mime_type") or "image/jpeg"
						return f"data:{mime};base64,{candidate}"
					return candidate

		return None


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

	@field_validator("cover_image", mode="before")
	@classmethod
	def normalize_cover_image(cls, value):
		if value is None:
			return None

		if isinstance(value, str):
			return value

		if isinstance(value, dict):
			if not value:
				return None

			for key in ("data_url", "url", "value", "base64"):
				candidate = value.get(key)
				if isinstance(candidate, str):
					if key == "base64":
						mime = value.get("mime_type") or "image/jpeg"
						return f"data:{mime};base64,{candidate}"
					return candidate

		return None


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
