import secrets
import uuid
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pymongo import ReturnDocument

from lib.db import db
from lib.demo_data import password_hash, verify_password
from models.auth import (
    AuthResponse, AuthUser, ForgotPasswordRequest, LoginRequest, ResetPasswordRequest,
    SignupRequest, VerifyOtpRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_COOKIE = "stocksense_session"
sessions: dict[str, str] = {}
pending_codes: dict[str, str] = {}


def public_user(doc: dict) -> AuthUser:
    return AuthUser(id=doc["id"], email=doc["email"], name=doc["name"], role=doc["role"])


async def current_user(session: str | None = Cookie(default=None, alias=SESSION_COOKIE)) -> dict:
    email = sessions.get(session or "")
    if not email:
        raise HTTPException(status_code=401, detail="Please sign in")
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Session expired")
    return user


async def manager_user(user: dict = Depends(current_user)) -> dict:
    if user.get("role") != "Inventory Manager":
        raise HTTPException(status_code=403, detail="Inventory Manager permission required")
    return user


def start_session(response: Response, user: dict) -> AuthUser:
    token = secrets.token_urlsafe(28)
    sessions[token] = user["email"]
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 7)
    return public_user(user)


@router.get("/me", response_model=AuthUser)
async def me(user: dict = Depends(current_user)):
    return public_user(user)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, response: Response):
    user = await db.users.find_one({"email": payload.email.lower().strip()})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return AuthResponse(user=start_session(response, user), message="Welcome back to StockSense")


@router.post("/signup", response_model=AuthResponse)
async def signup(payload: SignupRequest):
    email = payload.email.lower().strip()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    await db.users.insert_one({"id": str(uuid.uuid4()), "email": email, "name": payload.name.strip(), "role": "Warehouse Staff", "password_hash": password_hash(payload.password), "verified": False})
    pending_codes[email] = "123456"
    return AuthResponse(user=AuthUser(id="pending", email=email, name=payload.name, role="Warehouse Staff"), message="Verification code sent", verification_required=True, demo_code="123456")


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(payload: VerifyOtpRequest, response: Response):
    email = payload.email.lower().strip()
    if pending_codes.get(email) != payload.code:
        raise HTTPException(status_code=400, detail="That verification code is not valid")
    user = await db.users.find_one_and_update({"email": email}, {"$set": {"verified": True}}, return_document=ReturnDocument.AFTER)
    pending_codes.pop(email, None)
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    return AuthResponse(user=start_session(response, user), message="Your account is verified")


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    email = payload.email.lower().strip()
    if not await db.users.find_one({"email": email}):
        raise HTTPException(status_code=404, detail="No account found for that email")
    pending_codes[email] = "123456"
    return {"message": "Reset code generated", "demo_code": "123456"}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    email = payload.email.lower().strip()
    if pending_codes.get(email) != payload.code:
        raise HTTPException(status_code=400, detail="That reset code is not valid")
    await db.users.update_one({"email": email}, {"$set": {"password_hash": password_hash(payload.password), "verified": True}})
    pending_codes.pop(email, None)
    return {"message": "Password updated"}


@router.post("/logout")
async def logout(response: Response, session: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    sessions.pop(session or "", None)
    response.delete_cookie(SESSION_COOKIE)
    return {"message": "Signed out"}