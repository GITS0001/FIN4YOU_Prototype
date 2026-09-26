from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import copilot, users

app = FastAPI(title="FIN4YOU Prototype Backend", version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copilot.router, prefix="/api/copilot", tags=["Copilot"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FIN4YOU Prototype API v0.5.0"}
