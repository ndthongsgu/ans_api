import base64
import binascii
import json
import time

from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from models.listeningHistory import ListeningHistory
from models.owner import Owner
from models.stall import Stall
from models.stallContent import StallContent
from models.subscription_package import SubscriptionPackage
from models.stallTranslation import StallTranslation
from common.enums.language import LanguageCode
from modules.stall.dto.owner_dto import CreateStallRequest, StallResponse, UpdateStallRequest
from utils.translation import translate_text
from utils.file_helper import save_stall_image
import logging

logger = logging.getLogger(__name__)


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)

class OwnerStallService:
	def __init__(self, db: Session):
		self.db = db

	def _normalize_cover_image(self, cover_image: str | None) -> str | None:
		if cover_image is None:
			return None

		value = cover_image.strip()
		if not value:
			return None

		# Accept data URI images and store them in local static folder.
		if value.startswith("data:image/") and ";base64," in value:
			header, encoded = value.split(",", 1)
			ext = header[len("data:image/"):].split(";")[0].lower()
			ext = "jpg" if ext == "jpeg" else ext
			ext = "svg" if ext == "svg+xml" else ext
			if ext not in {"png", "jpg", "gif", "webp", "svg"}:
				raise ServiceError("invalid_cover_image")

			try:
				binary = base64.b64decode(encoded, validate=True)
			except (binascii.Error, ValueError):
				raise ServiceError("invalid_cover_image")

			# Keep uploads bounded to avoid abusive payloads.
			if len(binary) > 10 * 1024 * 1024:
				raise ServiceError("invalid_cover_image")

			try:
				return save_stall_image(binary, f"cover.{ext}")
			except Exception:
				raise ServiceError("invalid_cover_image")

		return value

	def _ensure_owner(self, user_id: str) -> Owner:
		owner = self.db.query(Owner).filter(Owner.user_id == user_id).first()
		if not owner:
			raise ServiceError("profile_not_found")
		return owner

	def _get_owned_stall(self, owner_id: str, stall_id: str) -> Stall:
		stall = (
			self.db.query(Stall)
			.filter(
				Stall.id == stall_id,
				Stall.owner_id == owner_id,
				Stall.is_deleted == False,
			)
			.first()
		)
		if not stall:
			raise ServiceError("stall_not_found")
		return stall

	def _get_stall_limit(self, owner: Owner) -> int:
		# Owners without a subscription package can create at most 3 stalls.
		default_limit = 3
		if not owner.subscription_package_id:
			return default_limit

		package = (
			self.db.query(SubscriptionPackage)
			.filter(
				SubscriptionPackage.id == owner.subscription_package_id,
				SubscriptionPackage.is_deleted == False,
			)
			.first()
		)
		if not package:
			return default_limit

		try:
			max_stalls = int(package.max_stalls or 0)
		except (TypeError, ValueError):
			max_stalls = 0
		return max_stalls if max_stalls > 0 else default_limit

	def get_stall_limit_info(self, user_id: str) -> dict:
		owner = self._ensure_owner(user_id)
		current_stalls = (
			self.db.query(Stall)
			.filter(Stall.owner_id == owner.id, Stall.is_deleted == False)
			.count()
		)
		limit = self._get_stall_limit(owner)
		return {
			"current_stalls": current_stalls,
			"max_stalls": limit,
			"remaining_stalls": max(limit - current_stalls, 0),
		}

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
			stall_name=stall.name,
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

	def list_stalls(self, user_id: str) -> list[StallResponse]:
		owner = self._ensure_owner(user_id)
		stalls = (
			self.db.query(Stall)
			.filter(Stall.owner_id == owner.id, Stall.is_deleted == False)
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
		limit = self._get_stall_limit(owner)
		current_stalls = (
			self.db.query(Stall)
			.filter(Stall.owner_id == owner.id, Stall.is_deleted == False)
			.count()
		)
		if current_stalls >= limit:
			raise ServiceError("stall_limit_exceeded")

		stall_name = payload.stall_name.strip()
		if not stall_name:
			raise ServiceError("invalid_stall_name")

		now = int(time.time())
		cover_image = self._normalize_cover_image(payload.cover_image)

		stall = Stall(
			owner_id=owner.id,
			name=stall_name,
			latitude=payload.latitude,
			longitude=payload.longitude,
			radius=payload.radius,
			cover_image=cover_image,
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
		self.db.flush()  # Get stall ID without committing yet
		
		# Create translations for all available languages
		for lang_info in LanguageCode.LIST:
			language_code = lang_info['code']
			
			try:
				# Try to translate name and category to target language
				if language_code == 'vi':
					# Vietnamese is the original language
					translated_name = stall_name
					translated_category = payload.category
				else:
					# Translate to other languages
					translated_name = translate_text(stall_name, 'vi', language_code)
					translated_category = None
					if payload.category:
						translated_category = translate_text(payload.category, 'vi', language_code)
				
				translation = StallTranslation(
					stall_id=stall.id,
					language_code=language_code,
					name=translated_name,
					category=translated_category,
				)
				self.db.add(translation)
				logger.info(f"[CREATE] {language_code}: {translated_name} | {translated_category}")
			
			except Exception as e:
				# If translation fails, fall back to Vietnamese text
				logger.warning(f"[FALLBACK] Translation failed for {language_code}: {str(e)}, using Vietnamese text")
				
				translation = StallTranslation(
					stall_id=stall.id,
					language_code=language_code,
					name=stall_name,
					category=payload.category,
				)
				self.db.add(translation)
		
		try:
			self.db.commit()
		except DataError as exc:
			self.db.rollback()
			if "cover_image" in str(exc).lower():
				raise ServiceError("invalid_cover_image")
			raise ServiceError("invalid_stall_payload")
		self.db.refresh(stall)
		return self._to_response(stall)

	def update_stall(self, user_id: str, stall_id: str, payload: UpdateStallRequest) -> StallResponse:
		owner = self._ensure_owner(user_id)
		stall = self._get_owned_stall(owner.id, stall_id)

		changes = payload.model_dump(exclude_unset=True)
		if "stall_name" in changes and changes["stall_name"] is not None:
			stall_name = changes["stall_name"].strip()
			if not stall_name:
				raise ServiceError("invalid_stall_name")
			stall.name = stall_name

		if "latitude" in changes:
			stall.latitude = changes["latitude"]
		if "longitude" in changes:
			stall.longitude = changes["longitude"]
		if "radius" in changes:
			stall.radius = changes["radius"]
		if "cover_image" in changes:
			stall.cover_image = self._normalize_cover_image(changes["cover_image"])
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
		
		# Update Vietnamese translation if name or category provided
		if "stall_name" in changes or "category" in changes:
			vi_translation = self.db.query(StallTranslation).filter(
				StallTranslation.stall_id == stall_id,
				StallTranslation.language_code == "vi"
			).first()
			
			if vi_translation:
				if "stall_name" in changes:
					vi_translation.name = changes["stall_name"]
				if "category" in changes:
					vi_translation.category = changes["category"]
				vi_translation.updated_at = int(time.time())
			else:
				# Create Vietnamese translation if it doesn't exist
				vi_translation = StallTranslation(
					stall_id=stall_id,
					language_code="vi",
					name=changes.get("stall_name", stall.name),
					category=changes.get("category", stall.category),
				)
				self.db.add(vi_translation)
			
			# Auto-translate to other languages when Vietnamese is updated
			for lang_info in LanguageCode.LIST:
				if lang_info['code'] == 'vi':
					continue  # Already handled Vietnamese above
				
				language_code = lang_info['code']
				
				try:
					# Translate Vietnamese name and category to target language
					translated_name = translate_text(changes.get("stall_name", stall.name), 'vi', language_code)
					translated_category = None
					if changes.get("category", stall.category):
						translated_category = translate_text(changes.get("category", stall.category), 'vi', language_code)
					
					# Update or create translation for this language
					other_translation = self.db.query(StallTranslation).filter(
						StallTranslation.stall_id == stall_id,
						StallTranslation.language_code == language_code
					).first()
					
					if other_translation:
						other_translation.name = translated_name
						other_translation.category = translated_category
						other_translation.updated_at = int(time.time())
					else:
						# Create translation if it doesn't exist
						other_translation = StallTranslation(
							stall_id=stall_id,
							language_code=language_code,
							name=translated_name,
							category=translated_category,
						)
						self.db.add(other_translation)
					
					logger.info(f"[UPDATE] {language_code}: {translated_name} | {translated_category}")
				
				except Exception as e:
					# If translation fails, fall back to Vietnamese text
					logger.warning(f"[FALLBACK] Translation failed for {language_code}: {str(e)}, using Vietnamese text")
					
					other_translation = self.db.query(StallTranslation).filter(
						StallTranslation.stall_id == stall_id,
						StallTranslation.language_code == language_code
					).first()
					
					if other_translation:
						other_translation.name = changes.get("stall_name", stall.name)
						other_translation.category = changes.get("category", stall.category)
						other_translation.updated_at = int(time.time())
					else:
						other_translation = StallTranslation(
							stall_id=stall_id,
							language_code=language_code,
							name=changes.get("stall_name", stall.name),
							category=changes.get("category", stall.category),
						)
						self.db.add(other_translation)
		
		try:
			self.db.commit()
		except DataError as exc:
			self.db.rollback()
			if "cover_image" in str(exc).lower():
				raise ServiceError("invalid_cover_image")
			raise ServiceError("invalid_stall_payload")
		self.db.refresh(stall)
		return self._to_response(stall)

	def delete_stall(self, user_id: str, stall_id: str) -> None:
		owner = self._ensure_owner(user_id)
		stall = self._get_owned_stall(owner.id, stall_id)

		contents = (
			self.db.query(StallContent)
			.filter(StallContent.stall_id == stall.id)
			.all()
		)

		if contents:
			content_ids = [content.id for content in contents]
			self.db.query(ListeningHistory).filter(
				ListeningHistory.stall_content_id.in_(content_ids)
			).delete(synchronize_session=False)
			for content in contents:
				self.db.delete(content)

		stall.is_deleted = True
		stall.updated_at = int(time.time())
		self.db.commit()