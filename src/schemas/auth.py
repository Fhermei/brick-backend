from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ── Signup ────────────────────────────────────────────────
class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, example="John Doe")
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=8, example="StrongPass123!")


class SignupResponse(BaseModel):
    message: str
    email: str


# ── Verify Email ──────────────────────────────────────────
class VerifyEmailRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    code: str = Field(..., min_length=6, max_length=6, example="123456")


class VerifyEmailResponse(BaseModel):
    message: str


# ── Login ─────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=8, example="StrongPass123!")


class LoginResponse(BaseModel):
    message: str
    email: str
    access_token: Optional[str] = None


# ── Refresh Token ─────────────────────────────────────────
class RefreshResponse(BaseModel):
    message: str


# ── Change Password ───────────────────────────────────────
class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8, example="OldPass123!")
    new_password: str = Field(..., min_length=8, example="NewPass456!")


class ChangePasswordResponse(BaseModel):
    message: str


# ── Forgot Password ───────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")


class ForgotPasswordResponse(BaseModel):
    message: str


# ── Confirm Forgot Password ───────────────────────────────
class ConfirmForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    code: str = Field(..., min_length=6, max_length=6, example="123456")
    new_password: str = Field(..., min_length=8, example="NewPass456!")


class ConfirmForgotPasswordResponse(BaseModel):
    message: str


# ── Me ────────────────────────────────────────────────────
class MeResponse(BaseModel):
    id: str
    name: str
    email: str
    is_verified: bool