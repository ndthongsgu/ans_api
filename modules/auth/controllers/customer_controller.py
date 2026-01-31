from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.services.customer_service import CustomerService
from modules.auth.dto.customer_dto import RegisterRequest, LoginRequest, TokenResponse
from utils.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth")

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = CustomerService(db)
    user = service.authenticate_customer(payload.username_or_email, payload.password)
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
