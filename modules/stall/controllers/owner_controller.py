from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
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


def _ensure_owner_role(current_user: User, locale: str | None):
	if not any(role.code == "OWNER" for role in current_user.roles):
		raise HTTPException(status_code=403, detail=t("forbidden", locale))


@router.get("", response_model=list[StallResponse])
def list_my_stalls(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	_ensure_owner_role(current_user, locale)
	service = OwnerStallService(db)
	return service.list_stalls(current_user.id)


@router.post("", response_model=StallResponse)
def create_stall(
	payload: CreateStallRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	_ensure_owner_role(current_user, locale)
	service = OwnerStallService(db)

	try:
		return service.create_stall(current_user.id, payload)
	except ServiceError as exc:
		if exc.code == "profile_not_found":
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/{stall_id}", response_model=StallResponse)
def get_stall_detail(
	stall_id: str,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	_ensure_owner_role(current_user, locale)
	service = OwnerStallService(db)

	try:
		return service.get_stall_detail(current_user.id, stall_id)
	except ServiceError as exc:
		if exc.code in {"profile_not_found", "stall_not_found"}:
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.put("/{stall_id}", response_model=StallResponse)
def update_stall(
	stall_id: str,
	payload: UpdateStallRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	_ensure_owner_role(current_user, locale)
	service = OwnerStallService(db)

	try:
		return service.update_stall(current_user.id, stall_id, payload)
	except ServiceError as exc:
		if exc.code in {"profile_not_found", "stall_not_found"}:
			raise HTTPException(status_code=404, detail=t(exc.code, locale))
		raise HTTPException(status_code=400, detail=t(exc.code, locale))
