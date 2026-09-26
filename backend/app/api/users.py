from fastapi import APIRouter, HTTPException
from typing import Optional, List
from app.ingestion.loader import DataLoader
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.schemas.financial import FinancialState, PredictionEngineResult, FinancialProfile
from app.schemas.decision import AffordabilityResult
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.schemas.decision import ScenarioResult, ExpectedImpact
from pydantic import BaseModel
from collections import defaultdict
from datetime import date
import math

router = APIRouter()

loader = DataLoader("data/prototype")
profiles = loader.load_profiles()
events = loader.load_events()


class MonthlyDataPoint(BaseModel):
    month: str
    income: float
    variable_expenses: float
    known_obligations: float
    cash_flow: float
    is_projected: bool = False


class MonthlyHistoryResponse(BaseModel):
    user_id: str
    observed_months: int
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    history: List[MonthlyDataPoint]
    projected: Optional[MonthlyDataPoint] = None


class AffordabilityRequest(BaseModel):
    amount: float


class WhatIfRequest(BaseModel):
    scenario_type: str  # "reduce_expense" or "add_purchase"
    amount: float


class WhatIfResponse(BaseModel):
    baseline: ScenarioResult
    scenario: ScenarioResult
    impact: ExpectedImpact
    currency: str


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


@router.get("/{user_id}/forecast/history", response_model=MonthlyHistoryResponse)
def get_forecast_history(user_id: str):
    """
    Returns monthly historical income/expense/cash_flow data plus the next-month projection.
    Used by the Forecast page chart to show OBSERVED history vs PROJECTED next month.
    """
    profile = next((p for p in profiles if p.user_id == user_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    user_events = [e for e in events if e.user_id == user_id]
    if not user_events:
        return MonthlyHistoryResponse(user_id=user_id, observed_months=0, history=[])

    # Build monthly buckets
    def get_month_key(d: date) -> str:
        return f"{d.year}-{d.month:02d}"

    monthly_income: dict = defaultdict(float)
    monthly_variable_expenses: dict = defaultdict(float)
    monthly_obligations: dict = defaultdict(float)

    for t in user_events:
        month_key = get_month_key(t.event_date)
        if t.event_type == "income":
            monthly_income[month_key] += t.amount
        elif t.event_type == "refund":
            if t.flexibility != "fixed" and t.event_type not in ["subscription", "debt_payment"]:
                monthly_variable_expenses[month_key] -= t.amount
        elif t.direction == "debit":
            if t.flexibility == "fixed" or t.event_type in ["subscription", "debt_payment"]:
                monthly_obligations[month_key] += t.amount
            else:
                monthly_variable_expenses[month_key] += t.amount

    all_months = sorted(set(
        list(monthly_income.keys()) +
        list(monthly_variable_expenses.keys()) +
        list(monthly_obligations.keys())
    ))

    history = []
    for month in all_months:
        inc = monthly_income.get(month, 0.0)
        var_exp = monthly_variable_expenses.get(month, 0.0)
        obs = monthly_obligations.get(month, 0.0)
        cf = inc - var_exp - obs
        history.append(MonthlyDataPoint(
            month=month,
            income=round(inc, 2),
            variable_expenses=round(var_exp, 2),
            known_obligations=round(obs, 2),
            cash_flow=round(cf, 2),
            is_projected=False,
        ))

    # Add projection if available
    pred = PredictionEngine().run_prediction(user_events, profile)
    projected_point = None
    if pred.available and pred.projected_cash_flow:
        pcf = pred.projected_cash_flow
        # Determine next month label
        last_month = all_months[-1] if all_months else "2024-06"
        parts = last_month.split("-")
        yr, mo = int(parts[0]), int(parts[1])
        if mo == 12:
            next_month = f"{yr+1}-01"
        else:
            next_month = f"{yr}-{mo+1:02d}"

        projected_point = MonthlyDataPoint(
            month=next_month,
            income=round(pcf.projected_income, 2),
            variable_expenses=round(pcf.projected_expenses, 2),
            known_obligations=round(pcf.known_obligations, 2),
            cash_flow=round(pcf.projected_cash_flow, 2),
            is_projected=True,
        )

    period_start = all_months[0] if all_months else None
    period_end = all_months[-1] if all_months else None

    return MonthlyHistoryResponse(
        user_id=user_id,
        observed_months=len(all_months),
        period_start=period_start,
        period_end=period_end,
        history=history,
        projected=projected_point,
    )


@router.post("/{user_id}/affordability", response_model=AffordabilityResult)
def check_affordability(user_id: str, request: AffordabilityRequest):
    """
    Evaluate whether a user can afford a given purchase amount.
    Returns affordability status, resulting balance, shortfall, and viable payment options.
    """
    profile = next((p for p in profiles if p.user_id == user_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    if request.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")

    user_events = [e for e in events if e.user_id == user_id]
    pred = PredictionEngine().run_prediction(user_events, profile)

    # Load payment options for this user
    import pandas as pd
    po_list = []
    try:
        requests_df = pd.read_csv("data/prototype/requests.csv")
        payment_opts_df = pd.read_csv("data/prototype/request_payment_options.csv")
        req_id = None
        for _, r in requests_df.iterrows():
            if r["user_id"] == user_id and abs(r["requested_amount"] - request.amount) < 1.0:
                req_id = r["request_id"]
                break
        if req_id is not None and not payment_opts_df.empty:
            opts = payment_opts_df[payment_opts_df["request_id"] == req_id]
            from app.schemas.financial import PaymentOption
            for _, o in opts.iterrows():
                pfq = o["payment_frequency_days"]
                if pd.isna(pfq):
                    pfq = None
                po_list.append(PaymentOption(
                    payment_option_id=o["payment_option_id"],
                    request_id=o["request_id"],
                    payment_method=o["payment_method"],
                    payment_amount=o["payment_amount"],
                    number_of_payments=int(o["number_of_payments"]),
                    first_payment_date=o["first_payment_date"],
                    payment_frequency_days=pfq,
                    financing_fee=o["financing_fee"],
                    total_payable_amount=o["total_payable_amount"],
                ))
    except Exception:
        po_list = []

    aff_eng = AffordabilityEngine(profile, pred)
    result = aff_eng.evaluate_purchase(request.amount, po_list)
    return result


@router.post("/{user_id}/what-if", response_model=WhatIfResponse)
def run_what_if(user_id: str, request: WhatIfRequest):
    """
    Run a deterministic what-if simulation on the backend.
    scenario_type: "reduce_expense" or "add_purchase"
    amount: the amount to adjust
    """
    profile = next((p for p in profiles if p.user_id == user_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")

    if request.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")

    user_events = [e for e in events if e.user_id == user_id]
    pred = PredictionEngine().run_prediction(user_events, profile)

    if not pred.available or not pred.projected_cash_flow:
        raise HTTPException(status_code=422, detail=f"Insufficient data: {pred.reason}")

    sim = WhatIfSimulator(profile, pred)
    baseline = sim.baseline_scenario()

    if request.scenario_type == "reduce_expense":
        scenario = sim.simulate_reduce_discretionary_spending(request.amount)
    elif request.scenario_type == "add_purchase":
        # Treat a one-time purchase as an additional obligation
        scenario = sim.simulate_add_obligation(request.amount)
    else:
        raise HTTPException(status_code=422, detail="scenario_type must be 'reduce_expense' or 'add_purchase'")

    impact = ImpactEngine.calculate_impact(baseline, scenario)

    return WhatIfResponse(
        baseline=baseline,
        scenario=scenario,
        impact=impact,
        currency=profile.home_currency,
    )
