from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import ensure_owner
from models.owner import Owner
from models.user import User
from common.dto.response import success_response
from modules.auth.controllers.mobile_controller import get_current_user
from modules.auth.dto.owner_dto import (
	LoginRequest,
	RefreshRequest,
	RegisterRequest,
	TokenResponse,
	UpdateProfileRequest,
)
from modules.auth.services.owner_service import OwnerService, ServiceError
from utils.i18n import t
from utils.security import (
	ALGORITHM,
	SECRET_KEY,
	create_access_token,
	create_refresh_token,
	jwt,
)

router = APIRouter(prefix="/auth")


@router.post("/register")
def register(
	payload: RegisterRequest,
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	service = OwnerService(db)
	try:
		user, _owner = service.create_owner(payload)
	except ServiceError as e:
		raise HTTPException(status_code=400, detail=t(e.code, locale))

	access = create_access_token(user.id)
	refresh = create_refresh_token(user.id)
	return success_response(
		message="Đăng ký thành công",
		data={"accessToken": access, "refreshToken": refresh},
		status_code=201,
	)


@router.post("/login")
def login(
	payload: LoginRequest,
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	service = OwnerService(db)
	user = service.authenticate_owner(payload.username, payload.password)
	if not user:
		raise HTTPException(status_code=401, detail=t("invalid_credentials", locale))

	access = create_access_token(user.id)
	refresh = create_refresh_token(user.id)
	return success_response(
		message="Đăng nhập thành công",
		data={"accessToken": access, "refreshToken": refresh},
	)


@router.get("/me")
def me(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerService(db)
	owner = service.get_owner_profile(current_user.id)
	if not owner:
		raise HTTPException(status_code=404, detail=t("profile_not_found", locale))

	return success_response(
		message="Lấy dữ liệu thành công",
		data={
		"id": current_user.id,
		"username": current_user.username,
		"email": current_user.email,
		"roles": [r.code for r in current_user.roles],
		"owner": {
			"id": owner.id,
			"full_name": owner.full_name,
			"phone": owner.phone,
			"business_name": owner.business_name,
			"business_address": owner.business_address,
   			"subscription_package_id" : owner.subscription_package_id,
			"subscription_expires_at": owner.subscription_expires_at,
		},
		},
	)


@router.put("/me")
def update_me(
	payload: UpdateProfileRequest,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	ensure_owner(current_user, db, locale)
	service = OwnerService(db)
	try:
		user, owner = service.update_owner_profile(current_user.id, payload)
	except ServiceError as e:
		raise HTTPException(status_code=400, detail=t(e.code, locale))

	return success_response(
		message="Cập nhật thông tin thành công",
		data={
		"id": user.id,
		"username": user.username,
		"email": user.email,
		"roles": [r.code for r in user.roles],
		"owner": {
			"id": owner.id,
			"full_name": owner.full_name,
			"phone": owner.phone,
			"business_name": owner.business_name,
			"business_address": owner.business_address,
			"subscription_expires_at": owner.subscription_expires_at,
		},
		},
	)


@router.post("/refresh")
def refresh(
	payload: RefreshRequest,
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language
	try:
		payload_refresh = jwt.decode(payload.refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
		if payload_refresh.get("type") != "refresh":
			raise HTTPException(status_code=401, detail=t("invalid_token", locale))

		user_id = payload_refresh.get("sub")
		if not user_id:
			raise HTTPException(status_code=401, detail=t("invalid_token", locale))

		user = db.query(User).filter(User.id == user_id).first()
		owner = db.query(Owner).filter(Owner.user_id == user_id).first()
		if not user or not owner:
			raise HTTPException(status_code=401, detail=t("user_not_found", locale))

		access = create_access_token(user_id)
		refresh_token = create_refresh_token(user_id)
		return success_response(
			message="Làm mới token thành công",
			data={"accessToken": access, "refreshToken": refresh_token},
		)
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=401, detail=t("token_expired", locale))
	except jwt.InvalidTokenError:
		raise HTTPException(status_code=401, detail=t("invalid_token", locale))
