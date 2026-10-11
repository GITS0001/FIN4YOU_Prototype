import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.auth import get_password_hash
from app.models import User, Profile

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_fin4you.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    user = User(email="test@fin4you.ai", hashed_password=get_password_hash("password"), is_active=True, is_verified=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    profile = Profile(user_id=user.id, full_name="Test User")
    db.add(profile)
    db.commit()
    return user

@pytest.fixture
def test_user_token(client, test_user):
    response = client.post("/api/auth/login", data={"username": "test@fin4you.ai", "password": "password"})
    return response.json()["access_token"]
