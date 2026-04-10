from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import ensure_owner
from common.dto.response import success_response
from models.user import User
from modules.auth.controllers.owner_controller import get_current_user
from modules.stall.dto.owner_dto import (
	CreateStallRequest,
	StallResponse,
	UpdateStallRequest,
)
from modules.stall.services.owner_service import OwnerStallService, ServiceError
from utils.i18n import t

router = APIRouter(prefix="/stalls")


@router.get("")
def list_my_stalls(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerStallService(db)
	data = service.list_stalls(current_user.id)
	return success_response(message="Lấy dữ liệu thành công", data=data)


@router.get("/limit")
def get_stall_limit(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerStallService(db)

	try:
		return success_response(
			message="Lấy thông tin giới hạn số quán thành công",
			data=service.get_stall_limit_info(current_user.id),
		)
	except ServiceError as exc:
		if exc.code == "profile_not_found":
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.post("")
def create_stall(
	payload: CreateStallRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerStallService(db)

	try:
		data = service.create_stall(current_user.id, payload)
		return success_response(message="Tạo quán thành công", data=data, status_code=201)
	except ServiceError as exc:
		if exc.code == "profile_not_found":
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/{stall_id}")
def get_stall_detail(
	stall_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerStallService(db)

	try:
		data = service.get_stall_detail(current_user.id, stall_id)
		return success_response(message="Lấy dữ liệu thành công", data=data)
	except ServiceError as exc:
		if exc.code in {"profile_not_found", "stall_not_found"}:
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.put("/{stall_id}")
def update_stall(
	stall_id: str,
	payload: UpdateStallRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerStallService(db)

	try:
		data = service.update_stall(current_user.id, stall_id, payload)
		return success_response(message="Cập nhật quán thành công", data=data)
	except ServiceError as exc:
		if exc.code in {"profile_not_found", "stall_not_found"}:
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.delete("/{stall_id}")
def delete_stall(
	stall_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerStallService(db)

	try:
		service.delete_stall(current_user.id, stall_id)
		return success_response(message=t("delete_success", locale))
	except ServiceError as exc:
		if exc.code in {"profile_not_found", "stall_not_found"}:
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))
