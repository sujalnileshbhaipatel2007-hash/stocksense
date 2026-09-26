from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    id: str
    email: str
    name: str
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)
    name: str = Field(min_length=2)


class VerifyOtpRequest(BaseModel):
    email: str
    code: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    password: str = Field(min_length=6)


class AuthResponse(BaseModel):
    user: AuthUser
    message: str | None = None
    verification_required: bool = False
    demo_code: str | None = None