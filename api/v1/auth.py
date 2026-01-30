from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from services.admin.user_service import UserService
from schemas.admin.user import User
from pydantic import BaseModel
from utils.security import create_access_token, create_refresh_token, decode_token
from jwt import InvalidTokenError

router = APIRouter(prefix="/api/auth")

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register", response_model=User)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    # Kiểm tra cả username và email xem đã tồn tại chưa
    user_by_name = service.repository.find_by_username_or_email(payload.username)
    user_by_email = service.repository.find_by_username_or_email(payload.email)
    
    if user_by_name or user_by_email:
        raise HTTPException(status_code=400, detail="Username or Email already exists")
    
    return service.create_user(payload)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.authenticate_user(payload.username_or_email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"accessToken": access, "refreshToken": refresh}


@router.post("/refresh", response_model=TokenResponse)
def refresh(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing refresh token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return {"accessToken": access, "refreshToken": refresh}


@router.get("/me", response_model=User)
def me(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user