from pydantic import BaseModel, EmailStr, model_validator

class LoginRequest(BaseModel):
    # client may send either username or email
    username: str | None = None
    email: str | None = None
    password: str

    @model_validator(mode="before")
    def require_user(cls, values: dict):
        uoe = values.get('username')
        email = values.get('email')
        if not (uoe or email):
            raise ValueError('either username or email is required')
        if not uoe:
            # copy email into username field for service convenience
            values['username'] = email
        return values

class RefreshRequest(BaseModel):
    refreshToken: str

class RegisterRequest(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str
    full_name: str

class UserCreate(BaseModel):
    username: str | None = None
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
