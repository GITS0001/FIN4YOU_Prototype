from fastapi import APIRouter, HTTPException
from app.schemas.copilot import CopilotRequest, CopilotResponse
from app.copilot.orchestrator import CopilotOrchestrator

router = APIRouter()
orchestrator = CopilotOrchestrator()

@router.post("/query", response_model=CopilotResponse)
def query_copilot(request: CopilotRequest):
    if not request.user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    if not request.message:
        raise HTTPException(status_code=400, detail="Missing message")
    
    try:
        return orchestrator.process_query(request)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
