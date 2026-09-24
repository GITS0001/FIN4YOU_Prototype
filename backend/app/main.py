from fastapi import FastAPI
from app.api import copilot

app = FastAPI(title="FIN4YOU Prototype Backend", version="0.5.0")

app.include_router(copilot.router, prefix="/api/copilot", tags=["Copilot"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FIN4YOU Prototype API v0.5.0"}
