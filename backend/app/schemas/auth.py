from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    monthly_income: Optional[float] = 0.0
    family_size: Optional[int] = 1
    currency: Optional[str] = "USD"

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    profile: Optional[Profile] = None

    class Config:
        from_attributes = True

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class OTPResponse(BaseModel):
    message: str
    email: str
    # FOR PROTOTYPE ONLY - WE EXPOSE THIS SO UI CAN AUTO-FILL OR USER CAN COPY IT
    mock_otp: Optional[str] = None
