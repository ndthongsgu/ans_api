from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.services.mobile_service import MobileService, ServiceError
from modules.auth.services.verification_service import VerificationService, VerificationError
from modules.auth.services.password_reset_service import PasswordResetService, PasswordResetError
from modules.auth.dto.mobile_dto import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, VerifyRequest, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest, UpdateProfileRequest
from models.user import User
from utils.security import create_access_token, create_refresh_token, jwt, SECRET_KEY, ALGORITHM
from fastapi import Header
from utils.i18n import t
from modules.auth.dto.mobile_dto import DeviceLoginRequest


router = APIRouter(prefix="/auth")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail=t('invalid_token', locale))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail=t('user_not_found', locale))
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail=t('token_expired', locale))
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail=t('invalid_token', locale))

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    service = MobileService(db)
    user = service.authenticate_customer(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail=t('invalid_credentials', locale))

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"accessToken": access, "refreshToken": refresh}

from fastapi import Header


@router.post("/register")
def register(payload: RegisterRequest, accept_language: str | None = Header(None), db: Session = Depends(get_db)):
    locale = accept_language
    service = VerificationService(db)
    try:
        verification = service.create_verification(payload, locale=locale)
    except VerificationError as e:
        # Localize message
        from utils.i18n import t
        raise HTTPException(status_code=400, detail=t(e.code, locale))
    except RuntimeError as e:
        # Email sending/config error
        from utils.i18n import t
        raise HTTPException(status_code=500, detail=t('smtp_not_configured', accept_language))

    from utils.i18n import t
    return {"message": t('otp_sent', locale)}


@router.post("/verify", response_model=TokenResponse)
def verify(payload: VerifyRequest, accept_language: str | None = Header(None), db: Session = Depends(get_db)):
    locale = accept_language
    service = VerificationService(db)
    try:
        db_user, customer = service.verify_and_create(payload.email, payload.otp)
    except VerificationError as e:
        from utils.i18n import t
        raise HTTPException(status_code=400, detail=t(e.code, locale))

    access = create_access_token(db_user.id)
    refresh = create_refresh_token(db_user.id)
    return {"accessToken": access, "refreshToken": refresh}


@router.post('/forgot-password')
def forgot_password(payload: ForgotPasswordRequest, accept_language: str | None = Header(None), db: Session = Depends(get_db)):
    locale = accept_language
    service = PasswordResetService(db)
    try:
        service.create_reset(payload.email, locale=locale)
    except PasswordResetError as e:
        raise HTTPException(status_code=400, detail=t(e.code, locale))

    return {"message": t('reset_sent', locale)}


@router.post('/reset-password')
def reset_password(payload: ResetPasswordRequest, accept_language: str | None = Header(None), db: Session = Depends(get_db)):
    locale = accept_language
    service = PasswordResetService(db)
    try:
        service.verify_and_reset(payload.email, payload.otp, payload.new_password)
    except PasswordResetError as e:
        raise HTTPException(status_code=400, detail=t(e.code, locale))

    return {"message": t('reset_success', locale)}

@router.post('/change-password')
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    service = MobileService(db)
    try:
        service.change_password(current_user.id, payload.current_password, payload.new_password)
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=t(e.code, locale))

    return {"message": t('change_password_success', locale)}


@router.post('/update-profile')
def update_profile(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    service = MobileService(db)
    try:
        data = service.update_profile(
            current_user.id,
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            avatar_url=payload.avatar_url,
        )
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=t(e.code, locale))

    return {"message": t('update_profile_success', locale), "data": data}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    service = MobileService(db)
    customer = service.get_customer_profile(current_user.id)
    if not customer:
        raise HTTPException(status_code=404, detail=t('profile_not_found', locale))
    return customer


@router.post("/google-login", response_model=TokenResponse)
def google_login(payload: dict, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    """Google OAuth login endpoint - receives Google ID token from mobile app"""
    locale = accept_language
    try:
        id_token_str = payload.get("idToken")
        if not id_token_str:
            raise HTTPException(status_code=400, detail="idToken required")
        
        service = MobileService(db)
        user = service.authenticate_with_google(id_token_str)
        
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        return {"accessToken": access, "refreshToken": refresh}
    except ServiceError as e:
        from utils.i18n import t
        # If detailed message exists (e.g., from token validation), use it; otherwise translate the error code
        detail = e.message if e.message else t(e.code, locale)
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    try:
        payload_refresh = jwt.decode(payload.refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
        if payload_refresh.get("type") != "refresh":
            raise HTTPException(status_code=401, detail=t('invalid_token', locale))
        user_id = payload_refresh.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail=t('invalid_token', locale))
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail=t('user_not_found', locale))
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        return {"accessToken": access, "refreshToken": refresh}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail=t('token_expired', accept_language))
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail=t('invalid_token', accept_language))

@router.post("/login-device", response_model=TokenResponse)
def login_device(payload: DeviceLoginRequest, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    locale = accept_language
    service = MobileService(db)
    user = service.login_or_create_by_device(payload.device_id)
    if not user:
        raise HTTPException(status_code=500, detail="Lỗi khi tạo tài khoản")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"accessToken": access, "refreshToken": refresh}
