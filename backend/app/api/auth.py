from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Profile, OTP
from app.schemas.auth import Token, UserCreate, User as UserSchema, OTPVerifyRequest, OTPResponse
from app.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/register", response_model=OTPResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create empty profile
    db_profile = Profile(user_id=db_user.id, full_name=user.full_name)
    db.add(db_profile)

    # Generate OTP
    otp_code = str(random.randint(100000, 999999))
    hashed_otp = get_password_hash(otp_code)
    expiry = datetime.utcnow() + timedelta(minutes=10)

    db_otp = OTP(
        user_id=db_user.id,
        hashed_otp=hashed_otp,
        expiry=expiry,
        created_at=datetime.utcnow(),
        status="pending"
    )
    db.add(db_otp)
    db.commit()

    return {"message": "User registered successfully", "email": user.email, "mock_otp": otp_code}

@router.post("/verify-otp", response_model=Token)
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_record = db.query(OTP).filter(
        OTP.user_id == user.id,
        OTP.status == "pending"
    ).order_by(OTP.created_at.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="No pending OTP found")

    if otp_record.expiry < datetime.utcnow():
        otp_record.status = "expired"
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired")

    otp_record.attempt_count += 1

    if not verify_password(request.otp, otp_record.hashed_otp):
        if otp_record.attempt_count >= 3:
            otp_record.status = "failed"
            db.commit()
            raise HTTPException(status_code=400, detail="Max attempts reached. Please request a new OTP.")
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")

    otp_record.status = "verified"
    user.is_verified = True
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify your OTP.",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
