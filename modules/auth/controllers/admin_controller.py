from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.services.admin_service import AdminService
from modules.auth.dto.admin_dto import LoginRequest, TokenResponse, RefreshRequest
from utils.security import create_access_token, create_refresh_token, jwt, SECRET_KEY, ALGORITHM
from common.dto.response import success_response

router = APIRouter(prefix="/auth")

security = HTTPBearer()

from modules.auth.controllers.mobile_controller import get_current_user
from models.user import User


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    service = AdminService(db)
    # payload.username may actually contain email
    user = service.authenticate_admin(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không chính xác")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"accessToken": access, "refreshToken": refresh}


@router.post("/refresh", response_model=TokenResponse)
def refresh(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    try:
        # Extract refresh token from Authorization header
        refresh_token = credentials.credentials
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
        
        # Create new tokens
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        return {"accessToken": access, "refreshToken": refresh}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    # ensure user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    # return minimal user info
    data = {"id": current_user.id, "username": current_user.username, "email": current_user.email, "is_admin": current_user.is_admin}
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )
