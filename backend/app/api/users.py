from fastapi import APIRouter, HTTPException
from typing import Optional
from app.ingestion.loader import DataLoader
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.schemas.financial import FinancialState, PredictionEngineResult, FinancialProfile

router = APIRouter()

loader = DataLoader("data/prototype")
profiles = loader.load_profiles()
events = loader.load_events()

@router.get("/{user_id}/profile", response_model=FinancialProfile)
def get_user_profile(user_id: str):
    profile = next((p for p in profiles if p.user_id == user_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@router.get("/{user_id}/state", response_model=FinancialState)
def get_user_state(user_id: str):
    profile = next((p for p in profiles if p.user_id == user_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_events = [e for e in events if e.user_id == user_id]
    state = FinancialStateEngine(user_id).calculate_state(user_events)
    return state

@router.get("/{user_id}/prediction", response_model=PredictionEngineResult)
def get_user_prediction(user_id: str):
    profile = next((p for p in profiles if p.user_id == user_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_events = [e for e in events if e.user_id == user_id]
    pred = PredictionEngine().run_prediction(user_events, profile)
    return pred
