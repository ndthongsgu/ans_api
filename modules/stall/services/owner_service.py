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
from utils.translation_util import TranslationService


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)


class OwnerStallService:
	def __init__(self, db: Session):
		self.db = db
		self.translator = TranslationService()

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
		if isinstance(opening_hours, str):
			return opening_hours
		return json.dumps([item.model_dump() for item in opening_hours], ensure_ascii=False)

	def _normalize_price_range(self, value) -> str | None:
		if value is None:
			return None
		return str(value)

	def _normalize_language_code(self, language_code: str | None) -> str:
		if language_code is None:
			return "vi"
		return language_code.strip().lower()

	def _ensure_supported_language(self, language_code: str) -> str:
		normalized = self._normalize_language_code(language_code)
		if not LanguageCode.is_supported(normalized):
			raise ServiceError("invalid_language_code")
		return normalized

	def _resolve_target_languages(self, source_language: str, target_languages: list[str] | None) -> list[str]:
		if target_languages is None:
			return [code for code in LanguageCode.codes() if code != source_language]

		resolved: list[str] = []
		for code in target_languages:
			normalized = self._ensure_supported_language(code)
			if normalized != source_language and normalized not in resolved:
				resolved.append(normalized)

		return resolved

	def _upsert_content(
		self,
		stall_id: str,
		language_code: str,
		title: str,
		description: str | None,
		short_description: str | None,
		audio_url: str,
		audio_duration: int | None,
		audio_file_size: int | None,
		tts_script: str | None,
		version: int,
		is_deleted: bool,
		now: int,
	) -> StallContent:
		content = (
			self.db.query(StallContent)
			.filter(
				StallContent.stall_id == stall_id,
				StallContent.language_code == language_code,
			)
			.first()
		)

		if not content:
			content = StallContent(
				stall_id=stall_id,
				language_code=language_code,
				title=title,
				description=description,
				short_description=short_description,
				audio_url=audio_url,
				audio_duration=audio_duration,
				audio_file_size=audio_file_size,
				tts_script=tts_script,
				version=version,
				is_deleted=is_deleted,
				created_at=now,
				updated_at=now,
			)
			self.db.add(content)
			return content

		content.title = title
		content.description = description
		content.short_description = short_description
		content.audio_url = audio_url
		content.audio_duration = audio_duration
		content.audio_file_size = audio_file_size
		content.tts_script = tts_script
		content.version = version
		content.is_deleted = is_deleted
		content.updated_at = now
		return content

	def _translate_for_language(
		self,
		source_language: str,
		target_language: str,
		title: str,
		description: str | None,
		short_description: str | None,
		tts_script: str | None,
	) -> dict:
		return {
			"title": self.translator.translate_text(title, source_language, target_language) or title,
			"description": self.translator.translate_text(description, source_language, target_language),
			"short_description": self.translator.translate_text(short_description, source_language, target_language),
			"tts_script": self.translator.translate_text(tts_script, source_language, target_language),
		}

	def _parse_opening_hours(self, opening_hours: str | None) -> list[dict] | str | None:
		if not opening_hours:
			return None

		try:
			parsed = json.loads(opening_hours)
			if isinstance(parsed, list):
				return parsed
		except json.JSONDecodeError:
			return opening_hours

		return None

	def _to_response(self, stall: Stall) -> StallResponse:
		return StallResponse(
			id=stall.id,
			owner_id=stall.owner_id,
			name=stall.name,
			latitude=stall.latitude,
			longitude=stall.longitude,
			radius=stall.radius,
			cover_image=stall.cover_image,
			contact_phone=stall.contact_phone,
			website=stall.website,
			opening_hours=self._parse_opening_hours(stall.opening_hours),
			close_hours=stall.close_hours,
			category=stall.category,
			price_range=stall.price_range,
			average_rating=float(stall.average_rating or 0),
			total_reviews=int(stall.total_reviews or 0),
			created_at=stall.created_at,
			updated_at=stall.updated_at,
		)

	def _to_content_response(self, content: StallContent) -> StallContentResponse:
		return StallContentResponse(
			id=content.id,
			stall_id=content.stall_id,
			language_code=content.language_code,
			title=content.title,
			description=content.description,
			short_description=content.short_description,
			audio_url=content.audio_url,
			audio_duration=content.audio_duration,
			audio_file_size=content.audio_file_size,
			tts_script=content.tts_script,
			version=content.version,
			is_active=not content.is_deleted,
			created_at=content.created_at,
			updated_at=content.updated_at,
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

		now = int(time.time())
		stall = Stall(
			owner_id=owner.id,
			name=name,
			latitude=payload.latitude,
			longitude=payload.longitude,
			radius=payload.radius,
			cover_image=payload.cover_image,
			contact_phone=payload.contact_phone,
			website=payload.website,
			opening_hours=self._serialize_opening_hours(payload.opening_hours),
			close_hours=payload.close_hours,
			category=payload.category,
			price_range=self._normalize_price_range(payload.price_range),
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
		if "cover_image" in changes:
			stall.cover_image = changes["cover_image"]
		if "contact_phone" in changes:
			stall.contact_phone = changes["contact_phone"]
		if "website" in changes:
			stall.website = changes["website"]
		if "opening_hours" in changes:
			stall.opening_hours = self._serialize_opening_hours(changes["opening_hours"])
		if "close_hours" in changes:
			stall.close_hours = changes["close_hours"]
		if "category" in changes:
			stall.category = changes["category"]
		if "price_range" in changes:
			stall.price_range = self._normalize_price_range(changes["price_range"])

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
		audio_url = payload.audio_url.strip()
		if not title:
			raise ServiceError("invalid_stall_content_title")
		if not audio_url:
			raise ServiceError("invalid_audio_url")

		source_language = self._ensure_supported_language(payload.language_code)

		now = int(time.time())
		content = self._upsert_content(
			stall_id=stall_id,
			language_code=source_language,
			title=title,
			description=payload.description,
			short_description=payload.short_description,
			audio_url=audio_url,
			audio_duration=payload.audio_duration,
			audio_file_size=payload.audio_file_size,
			tts_script=payload.tts_script,
			version=payload.version,
			is_deleted=not payload.is_active,
			now=now,
		)

		if payload.auto_translate:
			target_languages = self._resolve_target_languages(source_language, payload.target_languages)
			for language in target_languages:
				translated = self._translate_for_language(
					source_language=source_language,
					target_language=language,
					title=title,
					description=payload.description,
					short_description=payload.short_description,
					tts_script=payload.tts_script,
				)

				self._upsert_content(
					stall_id=stall_id,
					language_code=language,
					title=translated["title"],
					description=translated["description"],
					short_description=translated["short_description"],
					audio_url=audio_url,
					audio_duration=payload.audio_duration,
					audio_file_size=payload.audio_file_size,
					tts_script=translated["tts_script"],
					version=payload.version,
					is_deleted=not payload.is_active,
					now=now,
				)

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
		effective_language = content.language_code
		if "language_code" in changes and changes["language_code"] is not None:
			effective_language = self._ensure_supported_language(changes["language_code"])
			content.language_code = effective_language
		if "title" in changes and changes["title"] is not None:
			title = changes["title"].strip()
			if not title:
				raise ServiceError("invalid_stall_content_title")
			content.title = title
		if "description" in changes:
			content.description = changes["description"]
		if "short_description" in changes:
			content.short_description = changes["short_description"]
		if "audio_url" in changes and changes["audio_url"] is not None:
			audio_url = changes["audio_url"].strip()
			if not audio_url:
				raise ServiceError("invalid_audio_url")
			content.audio_url = audio_url
		if "audio_duration" in changes:
			content.audio_duration = changes["audio_duration"]
		if "audio_file_size" in changes:
			content.audio_file_size = changes["audio_file_size"]
		if "tts_script" in changes:
			content.tts_script = changes["tts_script"]
		if "version" in changes:
			content.version = changes["version"]
		if "is_active" in changes:
			content.is_deleted = not changes["is_active"]

		content.updated_at = int(time.time())

		should_translate = bool(changes.get("auto_translate"))
		target_languages = changes.get("target_languages")
		if should_translate:
			resolved_targets = self._resolve_target_languages(effective_language, target_languages)
			for language in resolved_targets:
				translated = self._translate_for_language(
					source_language=effective_language,
					target_language=language,
					title=content.title,
					description=content.description,
					short_description=content.short_description,
					tts_script=content.tts_script,
				)

				self._upsert_content(
					stall_id=stall_id,
					language_code=language,
					title=translated["title"],
					description=translated["description"],
					short_description=translated["short_description"],
					audio_url=content.audio_url,
					audio_duration=content.audio_duration,
					audio_file_size=content.audio_file_size,
					tts_script=translated["tts_script"],
					version=content.version,
					is_deleted=content.is_deleted,
					now=content.updated_at,
				)

		self.db.commit()
		self.db.refresh(content)
		return self._to_content_response(content)
