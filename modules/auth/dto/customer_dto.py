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

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
