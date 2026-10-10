import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app as fastapi_app
from app.database import Base, get_db
import app.models  # Required to register models with Base

from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database for E2E testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(fastapi_app)

def test_full_e2e_flow():
    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides[get_db] = override_get_db

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # 1. User registers
    res = client.post("/api/auth/register", json={
        "email": "e2e@example.com",
        "password": "securepassword",
        "full_name": "E2E User"
    })
    assert res.status_code == 200
    data = res.json()
    mock_otp = data["mock_otp"]

    # 2. Access protected endpoint before verification (should fail)
    # Login allows us to get token, but token fails on get_current_user
    # Actually wait, login will fail because is_verified=False
    res_login = client.post("/api/auth/login", data={
        "username": "e2e@example.com",
        "password": "securepassword"
    })
    assert res_login.status_code == 403

    # 3. Verify OTP
    res_verify = client.post("/api/auth/verify-otp", json={
        "email": "e2e@example.com",
        "otp": mock_otp
    })
    assert res_verify.status_code == 200
    token = res_verify.json()["access_token"]

    # 4. Access protected endpoint (Profile)
    headers = {"Authorization": f"Bearer {token}"}
    res_profile = client.get("/api/users/profile", headers=headers)
    assert res_profile.status_code == 200
    assert res_profile.json()["full_name"] == "E2E User"
