import base64
import binascii
import hashlib
import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from core import config
from models.owner import Owner
from models.stall import Stall
from modules.stall.dto.owner_dto import (
	CreateStallRequest,
	StallResponse,
	UpdateStallRequest,
)


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)

class OwnerStallService:
	def __init__(self, db: Session):
		self.db = db

	def _upload_cover_image_to_cloudinary(self, data_uri: str) -> str:
		cloud_name = config.CLOUDINARY_CLOUD_NAME.strip()
		if not cloud_name:
			raise ServiceError("invalid_cover_image")

		upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
		timestamp = int(time.time())
		params = {
			"file": data_uri,
			"folder": config.CLOUDINARY_FOLDER,
		}

		upload_preset = config.CLOUDINARY_UPLOAD_PRESET.strip()
		api_key = config.CLOUDINARY_API_KEY.strip()
		api_secret = config.CLOUDINARY_API_SECRET.strip()

		if upload_preset:
			params["upload_preset"] = upload_preset
		elif api_key and api_secret:
			sign_parts = [f"folder={config.CLOUDINARY_FOLDER}", f"timestamp={timestamp}"]
			signature_payload = "&".join(sign_parts) + api_secret
			signature = hashlib.sha1(signature_payload.encode("utf-8")).hexdigest()
			params["api_key"] = api_key
			params["timestamp"] = timestamp
			params["signature"] = signature
		else:
			raise ServiceError("invalid_cover_image")

		encoded = urlencode(params).encode("utf-8")
		request = Request(upload_url, data=encoded, method="POST")
		request.add_header("Content-Type", "application/x-www-form-urlencoded")

		try:
			with urlopen(request, timeout=20) as response:
				payload = json.loads(response.read().decode("utf-8"))
		except Exception:
			raise ServiceError("invalid_cover_image")

		secure_url = payload.get("secure_url")
		if not isinstance(secure_url, str) or not secure_url.strip():
			raise ServiceError("invalid_cover_image")
		return secure_url

	def _normalize_cover_image(self, cover_image: str | None) -> str | None:
		if cover_image is None:
			return None

		value = cover_image.strip()
		if not value:
			return None

		# Accept data URI images and persist them as static files.
		if value.startswith("data:image/") and ";base64," in value:
			header, encoded = value.split(",", 1)
			ext = header[len("data:image/"):].split(";")[0].lower()
			ext = "jpg" if ext == "jpeg" else ext
			if ext not in {"png", "jpg", "gif", "webp", "svg+xml"}:
				raise ServiceError("invalid_cover_image")

			file_ext = "svg" if ext == "svg+xml" else ext
			try:
				binary = base64.b64decode(encoded, validate=True)
			except (binascii.Error, ValueError):
				raise ServiceError("invalid_cover_image")

			# Keep uploads bounded to avoid abusive payloads.
			if len(binary) > 10 * 1024 * 1024:
				raise ServiceError("invalid_cover_image")

			# Upload to Cloudinary and keep the secure URL in database.
			return self._upload_cover_image_to_cloudinary(value)

		return value

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

		now = int(time.time())
		cover_image = self._normalize_cover_image(payload.cover_image)

		stall = Stall(
			owner_id=owner.id,
			name=name,
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
		try:
			self.db.commit()
		except DataError as exc:
			self.db.rollback()
			if "cover_image" in str(exc).lower():
				raise ServiceError("invalid_cover_image")
			raise ServiceError("invalid_stall_payload")
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
