from pydantic import BaseModel, Field, model_validator


class OpeningHourItem(BaseModel):
	dayOfWeek: int = Field(ge=0, le=6)
	openTime: str | None = None
	closeTime: str | None = None
	closed: bool = False

	@model_validator(mode="after")
	def validate_time_range(self):
		if not self.closed and (not self.openTime or not self.closeTime):
			raise ValueError("openTime and closeTime are required when closed is false")
		return self


class CreateStallRequest(BaseModel):
	name: str = Field(min_length=1, max_length=255)
	latitude: float = Field(ge=-90, le=90)
	longitude: float = Field(ge=-180, le=180)
	radius: int = Field(default=50, ge=1)
	coverImage: str | None = None
	openingHours: list[OpeningHourItem] | None = None
	category: str | None = Field(default=None, max_length=100)
	priceRange: str | None = Field(default=None, max_length=20)
	contactPhone: str | None = Field(default=None, max_length=20)
	website: str | None = Field(default=None, max_length=255)


class UpdateStallRequest(BaseModel):
	name: str | None = Field(default=None, min_length=1, max_length=255)
	latitude: float | None = Field(default=None, ge=-90, le=90)
	longitude: float | None = Field(default=None, ge=-180, le=180)
	radius: int | None = Field(default=None, ge=1)
	coverImage: str | None = None
	openingHours: list[OpeningHourItem] | None = None
	category: str | None = Field(default=None, max_length=100)
	priceRange: str | None = Field(default=None, max_length=20)
	contactPhone: str | None = Field(default=None, max_length=20)
	website: str | None = Field(default=None, max_length=255)
	status: bool | None = None


class StallResponse(BaseModel):
	id: str
	ownerId: str
	name: str
	latitude: float
	longitude: float
	radius: int
	coverImage: str | None = None
	contactPhone: str | None = None
	website: str | None = None
	openingHours: list[OpeningHourItem] | None = None
	category: str | None = None
	priceRange: str | None = None
	averageRating: float
	totalReviews: int
	status: bool
	createdAt: int
	updatedAt: int | None = None


class CreateStallContentRequest(BaseModel):
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


class UpdateStallContentRequest(BaseModel):
	languageCode: str | None = Field(default=None, min_length=2, max_length=10)
	title: str | None = Field(default=None, min_length=1, max_length=255)
	description: str | None = None
	shortDescription: str | None = Field(default=None, max_length=500)
	audioUrl: str | None = Field(default=None, min_length=1, max_length=500)
	audioDuration: int | None = Field(default=None, ge=0)
	audioFileSize: int | None = Field(default=None, ge=0)
	ttsScript: str | None = None
	version: int | None = Field(default=None, ge=1)
	isActive: bool | None = None


class StallContentResponse(BaseModel):
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
