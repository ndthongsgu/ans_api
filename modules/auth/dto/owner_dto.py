from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str 
    password: str

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    business_name: str | None = None
    business_address: str | None = None


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    business_name: str | None = None
    business_address: str | None = None


class RefreshRequest(BaseModel):
    refreshToken: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str