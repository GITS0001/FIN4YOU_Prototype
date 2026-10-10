from fastapi import APIRouter, HTTPException
from typing import Optional, List
from app.services.db_service import get_user_profile, get_user_transactions
from app.financial.state import FinancialStateEngine
from app.ml.forecasting import PredictionEngine
from app.schemas.financial import FinancialState, PredictionEngineResult, GlobalFinancialState, FinancialOverrides, RiskStatus, Transaction, MonthlyStatementResponse
from app.schemas.decision import AffordabilityResult
from app.decision.affordability import AffordabilityEngine
from app.decision.simulation import WhatIfSimulator
from app.decision.impact import ImpactEngine
from app.schemas.decision import ScenarioResult, ExpectedImpact
from pydantic import BaseModel
from collections import defaultdict
from datetime import date
import math
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Profile, Transaction as DBTransaction
from app.supabase_config import is_supabase_configured
from app.services.supabase_repository import supabase_repository
from app.financial.report import MonthlyReportEngine
from app.schemas.planner import (
    ProbabilisticForecastRequest,
    ProbabilisticForecastResponse,
    PlanEvaluationRequest,
    PlanEvaluationResponse,
)
from app.decision.planner import ConstrainedPlannerEngine

router = APIRouter()


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
    projected: List[MonthlyDataPoint] = []


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


@router.get("/profile")
def read_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_supabase_configured():
        sp = supabase_repository.get_profile(str(current_user.id))
        if sp:
            def _parse_list(val):
                if isinstance(val, list): return val
                if isinstance(val, str) and val.strip(): return [x.strip() for x in val.split("|") if x.strip()]
                return []
            return {
                "user_id": str(current_user.id),
                "email": current_user.email,
                "home_currency": sp.get("home_currency", "USD"),
                "current_available_balance": float(sp.get("current_available_balance", 0.0)),
                "minimum_balance_to_keep": float(sp.get("minimum_balance_to_keep", 0.0)),
                "financial_priorities": _parse_list(sp.get("financial_priorities")),
                "expense_categories_to_protect": _parse_list(sp.get("expense_categories_to_protect")),
                "expense_categories_user_is_willing_to_reduce": _parse_list(sp.get("expense_categories_user_is_willing_to_reduce")),
                "expense_categories_user_is_willing_to_stop": _parse_list(sp.get("expense_categories_user_is_willing_to_stop")),
                "payment_methods_user_will_consider": _parse_list(sp.get("payment_methods_user_will_consider")),
                "max_installment_months": sp.get("max_installment_months", 12),
                "full_name": sp.get("full_name", "Demo User"),
                "age": str(sp.get("age", "30")),
                "marital_status": sp.get("marital_status", "Single"),
                "dependents": str(sp.get("dependents", "0")),
                "occupation": sp.get("occupation", "Professional"),
                "city_tier": sp.get("city_tier", "Tier 1"),
            }

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first() if db else None
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "home_currency": profile.home_currency,
        "current_available_balance": profile.current_available_balance,
        "minimum_balance_to_keep": profile.minimum_balance_to_keep,
        "financial_priorities": [p for p in profile.financial_priorities.split("|") if p.strip()] if profile.financial_priorities else [],
        "expense_categories_to_protect": [p for p in profile.expense_categories_to_protect.split("|") if p.strip()] if profile.expense_categories_to_protect else [],
        "expense_categories_user_is_willing_to_reduce": [p for p in profile.expense_categories_user_is_willing_to_reduce.split("|") if p.strip()] if profile.expense_categories_user_is_willing_to_reduce else [],
        "expense_categories_user_is_willing_to_stop": [p for p in profile.expense_categories_user_is_willing_to_stop.split("|") if p.strip()] if profile.expense_categories_user_is_willing_to_stop else [],
        "payment_methods_user_will_consider": [p for p in profile.payment_methods_user_will_consider.split("|") if p.strip()] if profile.payment_methods_user_will_consider else [],
        "max_installment_months": profile.max_installment_months,
        "full_name": profile.full_name,
        "age": profile.age,
        "marital_status": profile.marital_status,
        "dependents": profile.dependents,
        "occupation": profile.occupation,
        "city_tier": profile.city_tier,
    }

@router.put("/profile")
def update_user_profile(updated_profile: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if is_supabase_configured():
        try:
            supabase_repository.upsert_profile(str(current_user.id), updated_profile)
        except Exception:
            pass

    if db:
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if not profile:
            profile = Profile(user_id=current_user.id)
            db.add(profile)

        if "full_name" in updated_profile: profile.full_name = updated_profile["full_name"]
        if "age" in updated_profile: profile.age = updated_profile["age"]
        if "marital_status" in updated_profile: profile.marital_status = updated_profile["marital_status"]
        if "dependents" in updated_profile: profile.dependents = updated_profile["dependents"]
        if "occupation" in updated_profile: profile.occupation = updated_profile["occupation"]
        if "city_tier" in updated_profile: profile.city_tier = updated_profile["city_tier"]

        if "current_available_balance" in updated_profile: profile.current_available_balance = updated_profile["current_available_balance"]
        if "minimum_balance_to_keep" in updated_profile: profile.minimum_balance_to_keep = updated_profile["minimum_balance_to_keep"]

        if "financial_priorities" in updated_profile:
            profile.financial_priorities = "|".join(updated_profile["financial_priorities"]) if isinstance(updated_profile["financial_priorities"], list) else updated_profile["financial_priorities"]
        if "expense_categories_to_protect" in updated_profile:
            profile.expense_categories_to_protect = "|".join(updated_profile["expense_categories_to_protect"]) if isinstance(updated_profile["expense_categories_to_protect"], list) else updated_profile["expense_categories_to_protect"]
        if "expense_categories_user_is_willing_to_reduce" in updated_profile:
            profile.expense_categories_user_is_willing_to_reduce = "|".join(updated_profile["expense_categories_user_is_willing_to_reduce"]) if isinstance(updated_profile["expense_categories_user_is_willing_to_reduce"], list) else updated_profile["expense_categories_user_is_willing_to_reduce"]
        if "expense_categories_user_is_willing_to_stop" in updated_profile:
            profile.expense_categories_user_is_willing_to_stop = "|".join(updated_profile["expense_categories_user_is_willing_to_stop"]) if isinstance(updated_profile["expense_categories_user_is_willing_to_stop"], list) else updated_profile["expense_categories_user_is_willing_to_stop"]

        db.commit()
        db.refresh(profile)

    return read_user_profile(current_user=current_user, db=db)


class CreateTransactionRequest(BaseModel):
    description: str
    amount: float
    category: Optional[str] = "General"
    direction: Optional[str] = "debit"
    event_type: Optional[str] = "expense"
    event_date: Optional[str] = None
    currency: Optional[str] = "INR"
    flexibility: Optional[str] = "variable"


@router.get("/transactions", response_model=List[Transaction])
def read_user_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 100
):
    transactions = get_user_transactions(db, current_user.id)
    return transactions[:limit]


@router.post("/transactions", response_model=Transaction)
def create_user_transaction(
    tx_data: CreateTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import uuid
    from datetime import datetime as dt_cls
    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
    ev_date_str = tx_data.event_date or date.today().isoformat()
    try:
        ev_date = dt_cls.strptime(ev_date_str[:10], "%Y-%m-%d").date()
    except Exception:
        ev_date = date.today()

    new_tx = DBTransaction(
        transaction_id=tx_id,
        user_id=str(current_user.id),
        event_type=tx_data.event_type or ("income" if tx_data.direction == "credit" else "expense"),
        description=tx_data.description,
        category=tx_data.category or "General",
        direction=tx_data.direction or "debit",
        amount=abs(float(tx_data.amount)),
        currency=tx_data.currency or "INR",
        event_date=ev_date_str,
        settlement_date=ev_date_str,
        status="SETTLED",
        flexibility=tx_data.flexibility or "variable"
    )
    if db:
        db.add(new_tx)
        db.commit()

    return Transaction(
        transaction_id=tx_id,
        user_id=str(current_user.id),
        event_type=new_tx.event_type,
        description=new_tx.description,
        category=new_tx.category,
        direction=new_tx.direction,
        amount=new_tx.amount,
        currency=new_tx.currency,
        event_date=ev_date,
        settlement_date=ev_date,
        status=new_tx.status,
        flexibility=new_tx.flexibility
    )


@router.delete("/transactions/{transaction_id}")
def delete_user_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if db:
        tx = db.query(DBTransaction).filter(
            DBTransaction.transaction_id == transaction_id
        ).first()
        if tx:
            db.delete(tx)
            db.commit()
            return {"status": "success", "deleted_id": transaction_id}
    return {"status": "success", "deleted_id": transaction_id}



@router.get("/state", response_model=FinancialState)
def get_user_state(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)
    # Patch the user_id in the response to match the actual user's DB id
    state.user_id = str(current_user.id)

    if is_supabase_configured():
        try:
            supabase_repository.save_financial_summary(str(current_user.id), state.model_dump())
        except Exception:
            pass

    return state


@router.get("/prediction", response_model=PredictionEngineResult)
def get_user_prediction(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    pred = PredictionEngine().run_prediction(user_events, profile)

    if is_supabase_configured() and pred.available and pred.projected_cash_flows:
        try:
            for pcf in pred.projected_cash_flows:
                supabase_repository.save_forecast(
                    user_id=str(current_user.id),
                    forecast_data={
                        "forecast_period": pcf.period,
                        "projected_income": pcf.projected_income,
                        "projected_expenses": pcf.projected_expenses,
                        "known_obligations": pcf.known_obligations,
                        "projected_cash_flow": pcf.projected_cash_flow,
                        "uncertainty": 0.0,
                        "confidence": 1.0,
                        "raw_forecast": pred.model_dump()
                    }
                )
        except Exception:
            pass

    return pred

@router.get("/monthly-statement", response_model=MonthlyStatementResponse)
def get_monthly_statement(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    if not user_events:
        raise HTTPException(status_code=400, detail="No transactions available")

    def get_month_key(d: date) -> str:
        return f"{d.year}-{d.month:02d}"

    # Group by month
    from collections import defaultdict
    monthly_data = defaultdict(lambda: {"income": 0.0, "expenses": 0.0, "savings": 0.0, "categories": defaultdict(float)})
    obligations = []

    for t in user_events:
        mk = get_month_key(t.event_date)
        if t.event_type == "income":
            monthly_data[mk]["income"] += t.amount
        elif t.event_type == "refund":
            if t.flexibility != "fixed" and t.event_type not in ["subscription", "debt_payment"]:
                monthly_data[mk]["expenses"] -= t.amount
        elif t.direction == "debit":
            monthly_data[mk]["expenses"] += t.amount
            if t.category:
                monthly_data[mk]["categories"][t.category] += t.amount
            if t.flexibility == "fixed" or t.event_type in ["subscription", "debt_payment"]:
                # Only add unique ones
                if not any(o["description"] == t.description for o in obligations):
                    obligations.append({"description": t.description, "amount": t.amount})

    sorted_months = sorted(monthly_data.keys())
    if not sorted_months:
        raise HTTPException(status_code=400, detail="No valid monthly data")

    current_month_key = sorted_months[-1]
    prev_month_key = sorted_months[-2] if len(sorted_months) > 1 else None

    cm = monthly_data[current_month_key]
    cm["savings"] = cm["income"] - cm["expenses"]

    pm = monthly_data[prev_month_key] if prev_month_key else {"income": 0.0, "expenses": 0.0, "savings": 0.0, "categories": defaultdict(float)}
    pm["savings"] = pm["income"] - pm["expenses"]

    cat_changes = []
    all_cats = set(list(cm["categories"].keys()) + list(pm["categories"].keys()))
    for c in all_cats:
        c_val = cm["categories"].get(c, 0.0)
        p_val = pm["categories"].get(c, 0.0)
        cat_changes.append({
            "category": c,
            "current": round(c_val, 2),
            "previous": round(p_val, 2),
            "change": round(c_val - p_val, 2)
        })

    pred = PredictionEngine().run_prediction(user_events, profile)
    forecast_data = {}
    if pred.projected_cash_flows:
        forecast_data = {
            "next_month_income": round(pred.projected_cash_flows[0].projected_income, 2),
            "next_month_expenses": round(pred.projected_cash_flows[0].projected_expenses, 2),
        }
    statement_response = {
        "month": current_month_key,
        "income": {"current": round(cm["income"], 2), "previous": round(pm["income"], 2), "change": round(cm["income"] - pm["income"], 2)},
        "expenses": {"current": round(cm["expenses"], 2), "previous": round(pm["expenses"], 2), "change": round(cm["expenses"] - pm["expenses"], 2)},
        "savings": {"current": round(cm["savings"], 2), "previous": round(pm["savings"], 2), "change": round(cm["savings"] - pm["savings"], 2)},
        "cash_flow": {"current": round(cm["savings"], 2), "previous": round(pm["savings"], 2), "change": round(cm["savings"] - pm["savings"], 2)},
        "category_changes": cat_changes,
        "recurring_obligations": obligations,
        "anomalies": [a.model_dump() for a in pred.anomalies] if pred.anomalies else [],
        "forecast": forecast_data,
        "observations": ["Your spending has been analyzed deterministically."] if cm["expenses"] > pm["expenses"] else ["Great job managing your expenses!"],
        "recommendations": ["Review your largest discretionary categories."]
    }

    if is_supabase_configured():
        try:
            state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)
            rep = MonthlyReportEngine.generate_report(user_events, state)
            supabase_repository.save_monthly_report(str(current_user.id), rep)
        except Exception:
            pass

    return statement_response


@router.get("/forecast/history", response_model=MonthlyHistoryResponse)
def get_forecast_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns monthly historical income/expense/cash_flow data plus the next-month projection.
    Used by the Forecast page chart to show OBSERVED history vs PROJECTED next month.
    """
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    if not user_events:
        return MonthlyHistoryResponse(user_id=str(current_user.id), observed_months=0, history=[])

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
    projected_points = []

    if pred.available and pred.projected_cash_flows:
        for pcf in pred.projected_cash_flows:
            projected_points.append(MonthlyDataPoint(
                month=pcf.period,
                income=round(pcf.projected_income, 2),
                variable_expenses=round(pcf.projected_expenses, 2),
                known_obligations=round(pcf.known_obligations, 2),
                cash_flow=round(pcf.projected_cash_flow, 2),
                is_projected=True,
            ))

    period_start = all_months[0] if all_months else None
    period_end = all_months[-1] if all_months else None

    return MonthlyHistoryResponse(
        user_id=str(current_user.id),
        observed_months=len(all_months),
        period_start=period_start,
        period_end=period_end,
        history=history,
        projected=projected_points,
    )


@router.post("/affordability", response_model=AffordabilityResult)
def check_affordability(request: AffordabilityRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Evaluate whether a user can afford a given purchase amount.
    Returns affordability status, resulting balance, shortfall, and viable payment options.
    """
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    if request.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")

    user_events = get_user_transactions(db, current_user.id)
    pred = PredictionEngine().run_prediction(user_events, profile)

    # Load payment options for this user
    import pandas as pd
    po_list = []
    try:
        requests_df = pd.read_csv("data/prototype/requests.csv")
        payment_opts_df = pd.read_csv("data/prototype/request_payment_options.csv")
        req_id = None
        for _, r in requests_df.iterrows():
            if r["user_id"] == f"user_{current_user.id}" and abs(r["requested_amount"] - request.amount) < 1.0:
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


@router.post("/what-if", response_model=WhatIfResponse)
def run_what_if(request: WhatIfRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Run a deterministic what-if simulation on the backend.
    scenario_type: "reduce_expense" or "add_purchase"
    amount: the amount to adjust
    """
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    if request.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")

    user_events = get_user_transactions(db, current_user.id)
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

@router.post("/financial-state", response_model=GlobalFinancialState)
def calculate_global_financial_state(overrides: FinancialOverrides, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    from copy import deepcopy
    sim_profile = deepcopy(profile)

    if overrides.balance_override is not None:
        sim_profile.current_available_balance = overrides.balance_override
    if overrides.minimum_buffer_override is not None:
        sim_profile.minimum_balance_to_keep = overrides.minimum_buffer_override

    user_events = get_user_transactions(db, current_user.id)

    # Calculate current historical totals for scaling
    current_income = sum(e.amount for e in user_events if e.event_type == "income")
    current_expenses = 0.0
    for e in user_events:
        if e.direction == "debit":
            current_expenses += e.amount
        elif e.event_type == "refund":
            current_expenses -= e.amount

    sim_events = deepcopy(user_events)

    # Apply income scaling
    if overrides.income_override is not None and current_income > 0:
        income_scale = overrides.income_override / current_income
        for e in sim_events:
            if e.event_type == "income":
                e.amount = e.amount * income_scale

    # Apply expense scaling
    if overrides.expenses_override is not None and current_expenses > 0:
        expense_scale = overrides.expenses_override / current_expenses
        for e in sim_events:
            if e.direction == "debit":
                e.amount = e.amount * expense_scale
            elif e.event_type == "refund":
                e.amount = e.amount * expense_scale

    # Calculate updated state
    current_state = FinancialStateEngine(str(current_user.id)).calculate_state(sim_events)

    # Calculate updated prediction
    prediction = PredictionEngine().run_prediction(sim_events, sim_profile)

    # Risk
    buffer_status = "ok"
    cash_flow_status = "ok"
    if prediction.gap_detection:
        if prediction.gap_detection.detected:
            buffer_status = "breached"
    if prediction.projected_cash_flow:
        if prediction.projected_cash_flow.projected_cash_flow < 0:
            cash_flow_status = "negative"

    risk = RiskStatus(buffer_status=buffer_status, cash_flow_status=cash_flow_status)

    return GlobalFinancialState(
        user_id=str(current_user.id),
        currency=sim_profile.home_currency,
        baseline=sim_profile,
        current_state=current_state,
        prediction=prediction,
        risk=risk,
        confidence=current_state.data_quality_confidence,
        data_sources=["prototype_data", "user_overrides"]
    )


@router.get("/financial-summaries")
def get_persisted_financial_summaries(current_user: User = Depends(get_current_user)):
    """Retrieve persisted financial summaries from Supabase for the authenticated user."""
    if not is_supabase_configured():
        return []
    res = supabase_repository.get_financial_summary(str(current_user.id))
    return [res] if res else []


@router.get("/forecasts")
def get_persisted_forecasts(current_user: User = Depends(get_current_user)):
    """Retrieve persisted forecasts from Supabase for the authenticated user."""
    if not is_supabase_configured():
        return []
    res = supabase_repository.get_forecast(str(current_user.id))
    return [res] if res else []


@router.get("/monthly-reports")
def get_persisted_monthly_reports(current_user: User = Depends(get_current_user)):
    """Retrieve persisted monthly reports from Supabase for the authenticated user."""
    if not is_supabase_configured():
        return []
    return supabase_repository.get_monthly_reports(str(current_user.id))


@router.post("/forecast/probabilistic", response_model=ProbabilisticForecastResponse)
def get_probabilistic_forecast(
    request: ProbabilisticForecastRequest = ProbabilisticForecastRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Addition 2 — Probabilistic Cash-Flow Forecasting API.
    Produces multi-period distributions for income, essential and discretionary expenses,
    net cash flow, and cumulative balance over at least 6 months.
    Reports MAE, RMSE, interval coverage and width against baseline.
    Estimates probability of falling below declared minimum reserve.
    """
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    pred_engine = PredictionEngine()
    result = pred_engine.run_probabilistic_forecast(user_events, profile, request)

    # Persist latest forecast distribution to Supabase if configured
    if is_supabase_configured() and result.available and result.periods:
        try:
            for p in result.periods:
                supabase_repository.save_forecast(
                    user_id=str(current_user.id),
                    forecast_data={
                        "forecast_period": p.period,
                        "projected_income": p.projected_income.mean,
                        "projected_expenses": p.essential_expenses.mean + p.discretionary_expenses.mean,
                        "known_obligations": p.known_obligations,
                        "projected_cash_flow": p.projected_cash_flow.mean,
                        "uncertainty": p.projected_cumulative_balance.std_dev,
                        "confidence": result.confidence_level,
                        "evaluation_mae": result.evaluation_metrics.expense_mae if result.evaluation_metrics else None,
                        "evaluation_rmse": result.evaluation_metrics.expense_rmse if result.evaluation_metrics else None,
                        "raw_forecast": p.model_dump()
                    }
                )
        except Exception:
            pass

    return result


@router.post("/planner/evaluate", response_model=PlanEvaluationResponse)
def evaluate_financial_plan(
    request: PlanEvaluationRequest = PlanEvaluationRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Addition 1 — Constrained Financial Action Planning API.
    Compares candidate action sequences across >= 6 monthly periods.
    Evaluates period-by-period balances, trade-offs, and shortfall probabilities.
    Identifies infeasible goals and explains conflicts with proposed relaxations.
    Recommends safest viable plan considering forecast uncertainty.
    """
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    planner = ConstrainedPlannerEngine()
    return planner.evaluate_plans(user_events, profile, request)
