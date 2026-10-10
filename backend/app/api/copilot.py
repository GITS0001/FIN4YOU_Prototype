from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.copilot.orchestrator import CopilotOrchestrator
from app.auth import get_current_user
from app.models import User
from app.database import get_db

router = APIRouter()
orchestrator = CopilotOrchestrator()

@router.post("/query", response_model=CopilotResponse)
def query_copilot(request: CopilotRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    request.user_id = str(current_user.id)
    if not request.message:
        raise HTTPException(status_code=400, detail="Missing message")
    
    try:
        return orchestrator.process_query(request, db)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
