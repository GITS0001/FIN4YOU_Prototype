from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Create a data directory for the sqlite DB if it doesn't exist
os.makedirs("data", exist_ok=True)

SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/fin4you.db")

# For sqlite, we need check_same_thread=False. For PostgreSQL, we don't.
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
