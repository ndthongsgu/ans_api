from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.services.customer_service import CustomerService
from modules.auth.dto.customer_dto import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from models.user import User
from utils.security import create_access_token, create_refresh_token, jwt, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = CustomerService(db)
    user = service.authenticate_customer(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return {"accessToken": access, "refreshToken": refresh}

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = CustomerService(db)
    try:
        db_user, customer = service.create_customer(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    access = create_access_token(db_user.id)
    refresh = create_refresh_token(db_user.id)
    return {"accessToken": access, "refreshToken": refresh}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = CustomerService(db)
    customer = service.get_customer_profile(current_user.id)
    return customer

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload_refresh = jwt.decode(payload.refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
        if payload_refresh.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload_refresh.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)
        return {"accessToken": access, "refreshToken": refresh}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
