from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.services.admin_service import AdminService
from modules.auth.dto.admin_dto import LoginRequest, TokenResponse
from utils.security import create_access_token, create_refresh_token
from utils.i18n import t

router = APIRouter(prefix="/auth")

from modules.auth.controllers.customer_controller import get_current_user
from models.user import User


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    service = AdminService(db)
    # payload.username may actually contain email
    user = service.authenticate_admin(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail=t('invalid_credentials', locale))

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"accessToken": access, "refreshToken": refresh}


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    # ensure user has ADMIN role
    if not any(r.code == "ADMIN" for r in current_user.roles):
        raise HTTPException(status_code=403, detail=t('forbidden', locale))
    # return minimal user info
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "roles": [r.code for r in current_user.roles]}
