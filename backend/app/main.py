from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import copilot, users, auth, plaid, alerts, statements
from app.database import engine, Base
from app.supabase_config import validate_supabase_env, is_supabase_configured, ENVIRONMENT

# In production, validate configuration immediately
validate_supabase_env()

# Initialize tables if local SQLite/Postgres ORM is bound
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(title="FIN4YOU Financial Health Copilot", version="0.6.0")

@app.on_event("startup")
def on_startup():
    validate_supabase_env()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copilot.router, prefix="/api/copilot", tags=["Copilot"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(plaid.router, prefix="/api/plaid", tags=["Plaid"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(statements.router, prefix="/api/statements", tags=["Statements"])

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "FIN4YOU Financial Health Copilot API v0.6.0",
        "persistence": "supabase" if is_supabase_configured() else "local"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "supabase_configured": is_supabase_configured()
    }
