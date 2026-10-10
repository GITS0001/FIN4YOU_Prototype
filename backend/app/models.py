from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    profile = relationship("Profile", back_populates="owner", uselist=False)

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hashed_otp = Column(String)
    expiry = Column(DateTime)
    attempt_count = Column(Integer, default=0)
    status = Column(String, default="pending") # pending, verified, expired, failed
    created_at = Column(DateTime)

    owner = relationship("User")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Personal Context (previously in localStorage)
    full_name = Column(String, index=True, default="Demo User")
    age = Column(String, default="30")
    marital_status = Column(String, default="Single")
    dependents = Column(String, default="0")
    occupation = Column(String, default="Professional")
    city_tier = Column(String, default="Tier 1")

    # Financial Profile
    home_currency = Column(String, default="USD")
    current_available_balance = Column(Float, default=0.0)
    minimum_balance_to_keep = Column(Float, default=0.0)

    # Comma-separated strings for lists
    financial_priorities = Column(String, default="")
    expense_categories_to_protect = Column(String, default="")
    expense_categories_user_is_willing_to_reduce = Column(String, default="")
    expense_categories_user_is_willing_to_stop = Column(String, default="")
    payment_methods_user_will_consider = Column(String, default="")
    max_installment_months = Column(Integer, default=12)

    owner = relationship("User", back_populates="profile")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String)
    description = Column(String)
    category = Column(String)
    direction = Column(String)
    amount = Column(Float)
    currency = Column(String)
    event_date = Column(Date)
    settlement_date = Column(Date, nullable=True)
    status = Column(String)
    flexibility = Column(String)
    ml_confidence = Column(Float, nullable=True)
    ml_status = Column(String, nullable=True)
    ml_confidence_level = Column(String, nullable=True)

    owner = relationship("User")

class CopilotRequest(Base):
    __tablename__ = "copilot_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    request_date = Column(Date)
    request_type = Column(String)
    requested_amount = Column(Float)
    desired_completion_date = Column(Date)
    allows_partial_payment = Column(Boolean)
    request_text = Column(String)

    owner = relationship("User")

class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(String, unique=True, index=True)
    access_token = Column(String)
    cursor = Column(String, nullable=True) # Used for transaction sync

    owner = relationship("User")
