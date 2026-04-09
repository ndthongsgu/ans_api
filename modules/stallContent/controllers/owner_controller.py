from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from common.dto.response import success_response

from core.database import get_db
from models.user import User
from modules.auth.controllers.mobile_controller import get_current_user
from modules.stallContent.dto.owner_dto import (
	StallContentResponse, 
	StallContentCreateRequest, 
	StallContentUpdateRequest,
	StallWithoutContentResponse,
	ToggleContentRequest
)
from modules.stallContent.services.owner_service import StallContentOwnerService
from utils.i18n import t

router = APIRouter(prefix="/stall-contents")


def _ensure_owner_role(current_user: User, locale: str | None):
	if not any(role.code == "OWNER" for role in current_user.roles):
		raise HTTPException(status_code=403, detail=t("forbidden", locale))


@router.get("/all", response_model=list[StallContentResponse])
def list_all_stall_contents(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	return service.list_all_contents(current_user.id)


@router.get("/available-stalls", response_model=list[StallWithoutContentResponse])
def get_available_stalls(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	return service.list_available_stalls(current_user.id)


@router.post("/")
def create_content(
	payload: StallContentCreateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	try:
		return service.create_content(current_user.id, payload.dict(exclude_unset=True))
	except RuntimeError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stall_id}/{content_id}")
def get_content_detail(
	stall_id: str,
	content_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	return service.get_detail(current_user.id, stall_id, content_id)


@router.put("/{stall_id}/{content_id}")
def update_content(
	stall_id: str,
	content_id: str,
	payload: StallContentUpdateRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	try:
		return service.update_content(current_user.id, stall_id, content_id, payload.dict(exclude_unset=True))
	except RuntimeError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{stall_id}/{content_id}")
def delete_content(
	stall_id: str,
	content_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	service.delete_content(current_user.id, stall_id, content_id)
	return success_response("Xóa nội dung thành công")


@router.patch("/{stall_id}/{content_id}/toggle")
def toggle_content(
	stall_id: str,
	content_id: str,
	payload: ToggleContentRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	
	is_del = payload.is_deleted
	if isinstance(is_del, str):
		is_del = is_del.lower() in ("true", "1", "yes")
		
	service.toggle_content(current_user.id, stall_id, content_id, is_del)
	return success_response("Cập nhật trạng thái thành công")


@router.get("/{stall_id}/available-languages")
def get_available_languages(
	stall_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	return service.get_available_languages(current_user.id, stall_id)


@router.get("/{stall_id}/language/{language_code}")
def listen_by_language(
	stall_id: str,
	language_code: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	_ensure_owner_role(current_user, accept_language)
	service = StallContentOwnerService(db)
	return service.get_by_language(current_user.id, stall_id, language_code)