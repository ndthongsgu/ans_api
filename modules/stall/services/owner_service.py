import json
import time

from sqlalchemy.orm import Session

from common.enums.language import LanguageCode
from models.owner import Owner
from models.stall import Stall
from models.stallContent import StallContent
from modules.stall.dto.owner_dto import (
	CreateStallContentRequest,
	CreateStallRequest,
	StallContentResponse,
	StallResponse,
	UpdateStallContentRequest,
	UpdateStallRequest,
)


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)


class OwnerStallService:
	def __init__(self, db: Session):
		self.db = db

	def _ensure_owner(self, user_id: str) -> Owner:
		owner = self.db.query(Owner).filter(Owner.user_id == user_id).first()
		if not owner:
			raise ServiceError("profile_not_found")
		return owner

	def _get_owned_stall(self, owner_id: str, stall_id: str) -> Stall:
		stall = (
			self.db.query(Stall)
			.filter(Stall.id == stall_id, Stall.owner_id == owner_id)
			.first()
		)
		if not stall:
			raise ServiceError("stall_not_found")
		return stall

	def _serialize_opening_hours(self, opening_hours) -> str | None:
		if opening_hours is None:
			return None
		return json.dumps([item.model_dump() for item in opening_hours], ensure_ascii=False)

	def _normalize_language_code(self, language_code: str | None) -> str:
		if language_code is None:
			return LanguageCode.DEFAULT
		return language_code.strip().lower()

	def _parse_opening_hours(self, opening_hours: str | None) -> list[dict] | None:
		if not opening_hours:
			return None

		try:
			parsed = json.loads(opening_hours)
			if isinstance(parsed, list):
				return parsed
		except json.JSONDecodeError:
			return None

		return None

	def _to_response(self, stall: Stall) -> StallResponse:
		return StallResponse(
			id=stall.id,
			ownerId=stall.owner_id,
			name=stall.name,
			latitude=stall.latitude,
			longitude=stall.longitude,
			radius=stall.radius,
			coverImage=stall.cover_image,
			contactPhone=stall.contact_phone,
			website=stall.website,
			openingHours=self._parse_opening_hours(stall.opening_hours),
			category=stall.category,
			priceRange=stall.price_range,
			averageRating=float(stall.average_rating or 0),
			totalReviews=int(stall.total_reviews or 0),
			status=bool(stall.status),
			createdAt=stall.created_at,
			updatedAt=stall.updated_at,
		)

	def _to_content_response(self, content: StallContent) -> StallContentResponse:
		return StallContentResponse(
			id=content.id,
			stallId=content.stall_id,
			languageCode=content.language_code,
			title=content.title,
			description=content.description,
			shortDescription=content.short_description,
			audioUrl=content.audio_url,
			audioDuration=content.audio_duration,
			audioFileSize=content.audio_file_size,
			ttsScript=content.tts_script,
			version=content.version,
			isActive=not content.is_deleted,
			createdAt=content.created_at,
			updatedAt=content.updated_at,
		)

	def _get_owned_content(self, owner_id: str, stall_id: str, content_id: str) -> StallContent:
		content = (
			self.db.query(StallContent)
			.join(Stall, Stall.id == StallContent.stall_id)
			.filter(
				StallContent.id == content_id,
				StallContent.stall_id == stall_id,
				Stall.owner_id == owner_id,
			)
			.first()
		)
		if not content:
			raise ServiceError("stall_content_not_found")
		return content

	def list_stalls(self, user_id: str) -> list[StallResponse]:
		owner = self._ensure_owner(user_id)
		stalls = (
			self.db.query(Stall)
			.filter(Stall.owner_id == owner.id)
			.order_by(Stall.created_at.desc())
			.all()
		)
		return [self._to_response(stall) for stall in stalls]

	def get_stall_detail(self, user_id: str, stall_id: str) -> StallResponse:
		owner = self._ensure_owner(user_id)
		stall = self._get_owned_stall(owner.id, stall_id)
		return self._to_response(stall)

	def create_stall(self, user_id: str, payload: CreateStallRequest) -> StallResponse:
		owner = self._ensure_owner(user_id)
		name = payload.name.strip()
		if not name:
			raise ServiceError("invalid_stall_name")

		# Check owner subscription package stall limit
		stall_count = self.db.query(Stall).filter(Stall.owner_id == owner.id).count()
		if owner.subscription_package is not None:
			if stall_count >= owner.subscription_package.max_stalls:
				raise ServiceError("stall_limit_reached")
		else:
			if stall_count >= 3:
				raise ServiceError("stall_limit_reached")

		now = int(time.time())
		stall = Stall(
			owner_id=owner.id,
			name=name,
			latitude=payload.latitude,
			longitude=payload.longitude,
			radius=payload.radius,
			cover_image=payload.coverImage,
			contact_phone=payload.contactPhone,
			website=payload.website,
			opening_hours=self._serialize_opening_hours(payload.openingHours),
			category=payload.category,
			price_range=payload.priceRange,
			status=True,
			created_at=now,
			updated_at=now,
		)

		self.db.add(stall)
		self.db.commit()
		self.db.refresh(stall)
		return self._to_response(stall)

	def update_stall(self, user_id: str, stall_id: str, payload: UpdateStallRequest) -> StallResponse:
		owner = self._ensure_owner(user_id)
		stall = self._get_owned_stall(owner.id, stall_id)

		changes = payload.model_dump(exclude_unset=True)
		if "name" in changes and changes["name"] is not None:
			name = changes["name"].strip()
			if not name:
				raise ServiceError("invalid_stall_name")
			stall.name = name

		if "latitude" in changes:
			stall.latitude = changes["latitude"]
		if "longitude" in changes:
			stall.longitude = changes["longitude"]
		if "radius" in changes:
			stall.radius = changes["radius"]
		if "coverImage" in changes:
			stall.cover_image = changes["coverImage"]
		if "contactPhone" in changes:
			stall.contact_phone = changes["contactPhone"]
		if "website" in changes:
			stall.website = changes["website"]
		if "openingHours" in changes:
			stall.opening_hours = self._serialize_opening_hours(changes["openingHours"])
		if "category" in changes:
			stall.category = changes["category"]
		if "priceRange" in changes:
			stall.price_range = changes["priceRange"]
		if "status" in changes:
			stall.status = changes["status"]

		stall.updated_at = int(time.time())
		self.db.commit()
		self.db.refresh(stall)
		return self._to_response(stall)

	def list_stall_contents(self, user_id: str, stall_id: str) -> list[StallContentResponse]:
		owner = self._ensure_owner(user_id)
		self._get_owned_stall(owner.id, stall_id)

		contents = (
			self.db.query(StallContent)
			.filter(StallContent.stall_id == stall_id)
			.order_by(StallContent.created_at.desc())
			.all()
		)
		return [self._to_content_response(content) for content in contents]

	def create_stall_content(
		self,
		user_id: str,
		stall_id: str,
		payload: CreateStallContentRequest,
	) -> StallContentResponse:
		owner = self._ensure_owner(user_id)
		self._get_owned_stall(owner.id, stall_id)

		title = payload.title.strip()
		audio_url = payload.audioUrl.strip()
		if not title:
			raise ServiceError("invalid_stall_content_title")
		if not audio_url:
			raise ServiceError("invalid_audio_url")

		now = int(time.time())
		content = StallContent(
			stall_id=stall_id,
			language_code=self._normalize_language_code(payload.languageCode),
			title=title,
			description=payload.description,
			short_description=payload.shortDescription,
			audio_url=audio_url,
			audio_duration=payload.audioDuration,
			audio_file_size=payload.audioFileSize,
			tts_script=payload.ttsScript,
			version=payload.version,
			is_deleted=not payload.isActive,
			created_at=now,
			updated_at=now,
		)

		self.db.add(content)
		self.db.commit()
		self.db.refresh(content)
		return self._to_content_response(content)

	def update_stall_content(
		self,
		user_id: str,
		stall_id: str,
		content_id: str,
		payload: UpdateStallContentRequest,
	) -> StallContentResponse:
		owner = self._ensure_owner(user_id)
		self._get_owned_stall(owner.id, stall_id)
		content = self._get_owned_content(owner.id, stall_id, content_id)

		changes = payload.model_dump(exclude_unset=True)
		if "languageCode" in changes and changes["languageCode"] is not None:
			content.language_code = self._normalize_language_code(changes["languageCode"])
		if "title" in changes and changes["title"] is not None:
			title = changes["title"].strip()
			if not title:
				raise ServiceError("invalid_stall_content_title")
			content.title = title
		if "description" in changes:
			content.description = changes["description"]
		if "shortDescription" in changes:
			content.short_description = changes["shortDescription"]
		if "audioUrl" in changes and changes["audioUrl"] is not None:
			audio_url = changes["audioUrl"].strip()
			if not audio_url:
				raise ServiceError("invalid_audio_url")
			content.audio_url = audio_url
		if "audioDuration" in changes:
			content.audio_duration = changes["audioDuration"]
		if "audioFileSize" in changes:
			content.audio_file_size = changes["audioFileSize"]
		if "ttsScript" in changes:
			content.tts_script = changes["ttsScript"]
		if "version" in changes:
			content.version = changes["version"]
		if "isActive" in changes:
			content.is_deleted = not changes["isActive"]

		content.updated_at = int(time.time())
		self.db.commit()
		self.db.refresh(content)
		return self._to_content_response(content)
