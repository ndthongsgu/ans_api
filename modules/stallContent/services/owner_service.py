from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from models.stallContent import StallContent
from models.stall import Stall
from models.owner import Owner
from models.stallContentTranslation import StallContentTranslation
from modules.stallContent.dto.owner_dto import StallContentResponse, StallWithoutContentResponse
from modules.stallContent.services.admin_service import StallContentService as AdminStallContentService
from utils.i18n import t


class StallContentOwnerService:
	def __init__(self, db: Session):
		self.db = db
		self.admin_service = AdminStallContentService(db)

	def _ensure_owner(self, user_id: str) -> Owner:
		owner = self.db.query(Owner).filter(Owner.user_id == user_id).first()
		if not owner:
			raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ chủ quán")
		return owner

	def _verify_owner_stall(self, owner_id: str, stall_id: str) -> Stall:
		stall = self.db.query(Stall).filter(Stall.id == stall_id, Stall.owner_id == owner_id).first()
		if not stall:
			raise HTTPException(status_code=403, detail="Không có quyền truy cập quán này")
		return stall

	def _verify_owner_content(self, owner_id: str, stall_id: str, content_id: str) -> StallContent:
		stall = self._verify_owner_stall(owner_id, stall_id)
		content = self.db.query(StallContent).filter(StallContent.id == content_id, StallContent.stall_id == stall.id).first()
		if not content:
			raise HTTPException(status_code=404, detail="Không tìm thấy nội dung thuyết minh")
		return content

	def _to_response(self, content: StallContent, trans: StallContentTranslation) -> StallContentResponse:
		stall_name = content.stall.name if content.stall else "Quán"
		script = trans.tts_script or content.tts_script or ""
		title = f"Thuyết minh {stall_name}"
		description = (script[:100] + "...") if len(script) > 100 else script

		return StallContentResponse(
			id=content.id,
			stall_id=content.stall_id,
			stall_name=stall_name,
			language_code=trans.language_code,
			title=title,
			description=description,
			audio_url=trans.audio_url,
			audio_duration=trans.audio_duration,
			audio_file_size=trans.audio_file_size,
			tts_script=script,
			version=content.version,
			is_deleted=content.is_deleted,
			created_at=content.created_at,
			updated_at=content.updated_at,
		)

	def list_all_contents(self, user_id: str) -> list[StallContentResponse]:
		owner = self._ensure_owner(user_id)
		contents = (
			self.db.query(StallContent)
			.join(Stall, Stall.id == StallContent.stall_id)
			.filter(Stall.owner_id == owner.id, Stall.status == True)
			.options(joinedload(StallContent.translations), joinedload(StallContent.stall))
			.order_by(StallContent.created_at.desc())
			.all()
		)

		responses = []
		for content in contents:
			# Get Vietnamese translation as primary display
			vi_trans = next((t for t in content.translations if t.language_code == "vi"), None)
			if vi_trans:
				responses.append(self._to_response(content, vi_trans))
			elif content.translations:
				# Fallback to any first translation
				responses.append(self._to_response(content, content.translations[0]))
		return responses

	def list_available_stalls(self, user_id: str) -> list[StallWithoutContentResponse]:
		owner = self._ensure_owner(user_id)
		stalls = self.db.query(Stall).filter(Stall.owner_id == owner.id, Stall.status == True).all()
		responses = []
		for stall in stalls:
			content = self.db.query(StallContent).filter(StallContent.stall_id == stall.id, StallContent.is_deleted == False).first()
			if not content:
				responses.append(StallWithoutContentResponse(stall_id=stall.id, stall_name=stall.name))
		return responses

	def create_content(self, user_id: str, data: dict) -> StallContentResponse:
		owner = self._ensure_owner(user_id)
		stall = self._verify_owner_stall(owner.id, data.get("stall_id"))
		created_contents = self.admin_service.create_stall_content(data)
		# admin_service returns [StallContent, Translation1, Translation2...]
		base_content = created_contents[0]
		base_content.stall = stall
		
		# Return the Vietnamese translation context
		vi_trans = next((t for t in created_contents[1:] if t.language_code == "vi"), created_contents[1] if len(created_contents) > 1 else None)
		if vi_trans:
			return self._to_response(base_content, vi_trans)
		
		raise HTTPException(status_code=500, detail="Không thể tạo dữ liệu dịch đa ngôn ngữ")

	def get_detail(self, user_id: str, stall_id: str, content_id: str) -> StallContentResponse:
		owner = self._ensure_owner(user_id)
		content = self._verify_owner_content(owner.id, stall_id, content_id)
		
		vi_trans = next((t for t in content.translations if t.language_code == "vi"), None)
		if not vi_trans and content.translations:
			vi_trans = content.translations[0]
			
		return self._to_response(content, vi_trans) if vi_trans else None

	def update_content(self, user_id: str, stall_id: str, content_id: str, data: dict) -> StallContentResponse:
		owner = self._ensure_owner(user_id)
		content = self._verify_owner_content(owner.id, stall_id, content_id)
		
		updated_contents = self.admin_service.update_stall_content(content.id, data)
		if not updated_contents:
			raise HTTPException(status_code=404, detail="Không cập nhật được")
			
		# Refresh from db to get relationships
		self.db.refresh(content)
		vi_trans = next((t for t in content.translations if t.language_code == "vi"), None)
		return self._to_response(content, vi_trans) if vi_trans else None

	def delete_content(self, user_id: str, stall_id: str, content_id: str):
		owner = self._ensure_owner(user_id)
		content = self._verify_owner_content(owner.id, stall_id, content_id)
		
		# Hard delete or delegate to admin_service? Admin service only provides deactivate.
		# Let's do hard delete to match the expectation or just deactivate it. 
		# The frontend calls Delete! I'll deactivate it for safety.
		self.admin_service.deactivate_stall_content(content.id)
		return True

	def toggle_content(self, user_id: str, stall_id: str, content_id: str, is_deleted: bool):
		owner = self._ensure_owner(user_id)
		content = self._verify_owner_content(owner.id, stall_id, content_id)
		if is_deleted:
			self.admin_service.deactivate_stall_content(content.id)
		else:
			self.admin_service.activate_stall_content(content.id)
		return True

	def get_available_languages(self, user_id: str, stall_id: str) -> list[str]:
		owner = self._ensure_owner(user_id)
		self._verify_owner_stall(owner.id, stall_id)
		return self.admin_service._get_all_language_codes()

	def get_by_language(self, user_id: str, stall_id: str, language_code: str) -> dict:
		owner = self._ensure_owner(user_id)
		stall = self._verify_owner_stall(owner.id, stall_id)
		
		content = self.db.query(StallContent).filter(StallContent.stall_id == stall.id, StallContent.is_deleted == False).order_by(StallContent.created_at.desc()).first()
		if not content:
			raise HTTPException(status_code=404, detail="Quán chưa có nội dung")
			
		trans = next((t for t in content.translations if t.language_code == language_code), None)
		if not trans:
			raise HTTPException(status_code=404, detail="Ngôn ngữ chưa có bản dịch")
			
		return {
			"audio_url": trans.audio_url,
			"tts_script": trans.tts_script,
			"language_code": trans.language_code
		}