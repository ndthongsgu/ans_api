from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str
    full_name: str

class UserCreate(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refreshToken: str

class VerifyRequest(BaseModel):
    email: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None

class GoogleLoginRequest(BaseModel):
    idToken: str

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str

class DeviceLoginRequest(BaseModel):
    device_id: str

