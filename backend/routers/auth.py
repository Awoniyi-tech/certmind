"""
auth.py — Authentication router for CertMind.

Handles user registration, login, and profile management.
Uses JWT tokens for stateless session management and bcrypt for password hashing.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from database.db import get_db

router = APIRouter()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET", "certmind-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class RegisterBody(BaseModel):
    email: str
    password: str
    name: str


class LoginBody(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    target_exam_date: Optional[str] = None
    study_goal: Optional[str] = None


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(user_id: str, email: str, name: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


# ---------------------------------------------------------------------------
# Auth dependency — inject into any protected route
# ---------------------------------------------------------------------------
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    """Extract and validate the current user from the JWT bearer token.

    Returns a dict with id, email, name.  Raises 401 if missing or invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    async with db.execute("SELECT id, email, name, created_at, target_exam_date, study_goal FROM users WHERE id = ?", (user_id,)) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="User not found.")

    return dict(row)


# Optional auth — returns None if no token present (for public routes)
async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            return None
        async with db.execute("SELECT id, email, name, created_at FROM users WHERE id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/register")
async def register(body: RegisterBody, db=Depends(get_db)):
    # Validate
    email = body.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Invalid email address.")
    if len(body.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")
    if not body.name.strip():
        raise HTTPException(400, "Name is required.")

    # Check duplicate
    async with db.execute("SELECT id FROM users WHERE email = ?", (email,)) as cur:
        if await cur.fetchone():
            raise HTTPException(409, "An account with this email already exists.")

    user_id = str(uuid.uuid4())
    hashed = pwd_context.hash(body.password)

    await db.execute(
        "INSERT INTO users (id, email, password, name) VALUES (?, ?, ?, ?)",
        (user_id, email, hashed, body.name.strip()),
    )
    await db.commit()

    token = create_access_token(user_id, email, body.name.strip())
    return {
        "token": token,
        "user": {"id": user_id, "email": email, "name": body.name.strip()},
    }


@router.post("/login")
async def login(body: LoginBody, db=Depends(get_db)):
    email = body.email.strip().lower()

    async with db.execute("SELECT * FROM users WHERE email = ?", (email,)) as cur:
        row = await cur.fetchone()

    if not row:
        raise HTTPException(401, "Invalid email or password.")

    user = dict(row)
    if not pwd_context.verify(body.password, user["password"]):
        raise HTTPException(401, "Invalid email or password.")

    token = create_access_token(user["id"], user["email"], user["name"])
    return {
        "token": token,
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
    }


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    return user


@router.put("/profile")
async def update_profile(body: ProfileUpdate, user=Depends(get_current_user), db=Depends(get_db)):
    updates = []
    params = []

    if body.name and body.name.strip():
        updates.append("name = ?")
        params.append(body.name.strip())

    if body.email and body.email.strip():
        new_email = body.email.strip().lower()
        # Check for duplicate
        async with db.execute("SELECT id FROM users WHERE email = ? AND id != ?", (new_email, user["id"])) as cur:
            if await cur.fetchone():
                raise HTTPException(409, "Email already in use.")
        updates.append("email = ?")
        params.append(new_email)

    if body.target_exam_date is not None:
        updates.append("target_exam_date = ?")
        params.append(body.target_exam_date.strip() if body.target_exam_date else None)

    if body.study_goal is not None:
        updates.append("study_goal = ?")
        params.append(body.study_goal.strip() if body.study_goal else None)

    if not updates:
        raise HTTPException(400, "Nothing to update.")

    params.append(user["id"])
    await db.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
    await db.commit()

    # Return updated user
    async with db.execute("SELECT id, email, name, created_at, target_exam_date, study_goal FROM users WHERE id = ?", (user["id"],)) as cur:
        row = await cur.fetchone()
    return dict(row)
