import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Profile
from app.supabase_config import is_supabase_configured, get_supabase_client

load_dotenv()

logger = logging.getLogger("fin4you.auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

DEFAULT_DEV_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
RAW_SECRET = os.getenv("SECRET_KEY", "").strip()

if ENVIRONMENT == "production":
    if not RAW_SECRET or RAW_SECRET == DEFAULT_DEV_SECRET or len(RAW_SECRET) < 32:
        raise RuntimeError(
            "CRITICAL SECURITY CONFIGURATION ERROR: Production mode requires an explicit, strong SECRET_KEY "
            "(minimum 32 characters) distinct from the development fallback."
        )
    SECRET_KEY = RAW_SECRET
else:
    SECRET_KEY = RAW_SECRET or DEFAULT_DEV_SECRET

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET") or os.getenv("JWT_SECRET") or ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Attempts to verify a Supabase access token.
    Checks JWT secret if available, or verifies via Supabase client auth.
    """
    if not is_supabase_configured():
        return None

    # Method 1: Decode JWT directly if SUPABASE_JWT_SECRET is configured
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], audience="authenticated")
            user_id = payload.get("sub")
            email = payload.get("email")
            if user_id:
                fallback_email = user_id if "@" in user_id else f"user_{user_id[:8]}@fin4you.ai"
                return {"user_id": user_id, "email": email or fallback_email}
        except JWTError:
            pass

    # Method 2: Call Supabase client auth.get_user(token)
    try:
        client = get_supabase_client(use_secret_key=False)
        if client:
            user_response = client.auth.get_user(token)
            if user_response and user_response.user:
                u = user_response.user
                return {"user_id": u.id, "email": u.email or f"user_{u.id[:8]}@fin4you.ai"}
    except Exception as e:
        logger.debug(f"Supabase auth get_user check failed: {type(e).__name__}")

    return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Validates token and returns authenticated User entity.
    Never trusts client-supplied user IDs.
    Supports both native JWT and Supabase Auth access tokens.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. First, check if it is a Supabase Auth token
    sb_user_info = verify_supabase_token(token)
    if sb_user_info:
        sb_email = sb_user_info.get("email")
        sb_uid = sb_user_info.get("user_id")

        # Synchronize with local DB session if available
        user = db.query(User).filter((User.email == sb_email) | (User.id == sb_uid)).first() if db else None
        if not user and db:
            user = User(email=sb_email, hashed_password="", is_active=True, is_verified=True)
            db.add(user)
            db.commit()
            db.refresh(user)

            # Ensure profile exists
            prof = db.query(Profile).filter(Profile.user_id == user.id).first()
            if not prof:
                db_prof = Profile(user_id=user.id, full_name="Supabase User")
                db.add(db_prof)
                db.commit()
        elif user and not user.is_verified:
            user.is_verified = True
            if db:
                db.commit()

        if user:
            return user

    # 2. Native JWT validation
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first() if db else None
    if user is None:
        raise credentials_exception
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify your OTP.",
        )
    return user
