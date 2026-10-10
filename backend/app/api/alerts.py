from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.services.db_service import get_user_profile, get_user_transactions
from app.financial.state import FinancialStateEngine
from typing import List, Dict, Any

router = APIRouter()

@router.get("", response_model=List[Dict[str, Any]])
def get_alerts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_user_profile(db, current_user.id)
    if not profile:
        return []

    user_events = get_user_transactions(db, current_user.id)
    state = FinancialStateEngine(profile.user_id).calculate_state(user_events)

    alerts = []

    # Check anomalies
    for anomaly in state.anomalies:
        if anomaly.is_anomaly:
            alerts.append({
                "id": anomaly.transaction_id,
                "type": "warning",
                "title": "Unusual Spending Detected",
                "message": anomaly.reason,
                "is_read": False,
                "timestamp": "Just now"
            })

    # Check cash flow breach
    if state.cash_flow < 0:
        alerts.append({
            "id": "cf-breach",
            "type": "danger",
            "title": "Negative Cash Flow",
            "message": "Your observed expenses exceeded your income for the period.",
            "is_read": False,
            "timestamp": "Just now"
        })

    return alerts
