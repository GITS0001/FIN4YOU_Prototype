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
    scenario_type: str  # "reduce_expense", "add_purchase", or "reduce_income"
    amount: float


class WhatIfResponse(BaseModel):
    scenario_type: str = "reduce_expense"
    baseline_income: float = 0.0
    baseline_expenses: float = 0.0
    baseline_net_cash_flow: float = 0.0
    applied_adjustment: float = 0.0
    scenario_income: float = 0.0
    scenario_expenses: float = 0.0
    scenario_net_cash_flow: float = 0.0
    projected_balance: Optional[float] = None
    minimum_buffer: Optional[float] = None
    buffer_status: str = "unknown"
    assumptions: List[str] = []
    limitations: List[str] = []
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
                "home_currency": sp.get("home_currency", "INR"),
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
        except Exception as e:
            import logging
            logging.getLogger("fin4you.users").error(f"Supabase profile write failed: {e}. Falling back to SQLite.")

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


@router.get("/transactions", response_model=List[Transaction])
def read_user_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    transactions = get_user_transactions(db, current_user.id)
    return transactions[:limit]


@router.get("/state", response_model=FinancialState)
def get_user_state(
    month: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    state = FinancialStateEngine(str(current_user.id)).calculate_state(
        transactions=user_events,
        profile=profile,
        month_filter=month
    )
    # Patch the user_id in the response to match the actual user's DB id
    state.user_id = str(current_user.id)

    if is_supabase_configured():
        try:
            supabase_repository.save_financial_summary(str(current_user.id), state.model_dump())
        except Exception as e:
            import logging
            logging.getLogger("fin4you.users").error(f"Supabase state write failed: {e}. No local fallback available.")

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
        except Exception as e:
            import logging
            logging.getLogger("fin4you.users").error(f"Supabase forecast write failed: {e}. No local fallback available.")

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
    state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)
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
        "anomalies": [a.model_dump() for a in state.anomalies] if state.anomalies else [],
        "forecast": forecast_data,
        "observations": ["Your spending has been analyzed deterministically."] if cm["expenses"] > pm["expenses"] else ["Great job managing your expenses!"],
        "recommendations": ["Review your largest discretionary categories."]
    }

    if is_supabase_configured():
        try:
            state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)
            rep = MonthlyReportEngine.generate_report(user_events, state)
            supabase_repository.save_monthly_report(str(current_user.id), rep)
        except Exception as e:
            import logging
            logging.getLogger("fin4you.users").error(f"Supabase monthly report write failed: {e}. No local fallback available.")

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
        state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)
        if state.income > 0 or state.expenses > 0:
            from app.schemas.financial import ProjectedCashFlow
            pcf = ProjectedCashFlow(
                period="Current Observed",
                projected_income=state.income,
                projected_expenses=state.discretionary_expenses + state.essential_expenses,
                known_obligations=state.recurring_obligations,
                projected_cash_flow=state.cash_flow,
            )
            pred = PredictionEngineResult(
                available=True,
                reason="Derived directly from actual financial state",
                projected_cash_flow=pcf,
                projected_cash_flows=[pcf]
            )
        else:
            raise HTTPException(status_code=422, detail=f"Insufficient data: {pred.reason or 'No transactions found'}")

    sim = WhatIfSimulator(profile, pred)
    baseline = sim.baseline_scenario()

    if request.scenario_type == "reduce_expense":
        scenario = sim.simulate_reduce_discretionary_spending(request.amount)
    elif request.scenario_type == "add_purchase":
        # Treat a one-time purchase as an additional obligation
        scenario = sim.simulate_add_obligation(request.amount)
    elif request.scenario_type == "reduce_income":
        scenario = sim.simulate_reduce_income(request.amount)
    else:
        raise HTTPException(status_code=422, detail="scenario_type must be 'reduce_expense', 'add_purchase', or 'reduce_income'")

    impact = ImpactEngine.calculate_impact(baseline, scenario)
    buffer_status = "breached" if scenario.buffer_breached else "maintained"
    min_buf = profile.minimum_balance_to_keep

    return WhatIfResponse(
        scenario_type=request.scenario_type,
        baseline_income=round(baseline.projected_income, 2),
        baseline_expenses=round(baseline.projected_expenses + baseline.known_obligations, 2),
        baseline_net_cash_flow=round(baseline.projected_cash_flow, 2),
        applied_adjustment=round(request.amount, 2),
        scenario_income=round(scenario.projected_income, 2),
        scenario_expenses=round(scenario.projected_expenses + scenario.known_obligations, 2),
        scenario_net_cash_flow=round(scenario.projected_cash_flow, 2),
        projected_balance=round(scenario.projected_balance, 2),
        minimum_buffer=round(min_buf, 2) if min_buf is not None else None,
        buffer_status=buffer_status,
        assumptions=[
            f"Projection based on monthly income of {profile.home_currency} {baseline.projected_income:,.2f}",
            f"Minimum safety buffer set to {profile.home_currency} {min_buf:,.2f}" if min_buf else "No minimum buffer specified",
        ],
        limitations=[
            "Deterministic single-period projection; unexpected emergency transactions not included.",
        ],
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

    # Calculate current baseline totals using deterministic financial engine
    base_state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)
    current_income = base_state.income
    current_expenses = base_state.expenses

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
        except Exception as e:
            import logging
            logging.getLogger("fin4you.users").error(f"Supabase probabilistic forecast write failed: {e}. No local fallback available.")

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


@router.get("/planner/90-day-plan")
def get_90_day_financial_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    90-Day Financial Action Plan API.
    Builds a personalized 90-day trajectory based on the user's dataset:
    - Calculates 3 phased 30-day savings milestones and actionable guidance.
    - Grounded in live income, essential/discretionary expenses, and buffer.
    - Provides financial terms glossary contextualized with the user's metrics.
    """
    profile = get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    user_events = get_user_transactions(db, current_user.id)
    state = FinancialStateEngine(str(current_user.id)).calculate_state(user_events)

    currency = getattr(profile, "home_currency", "INR") or "INR"
    available_balance = float(getattr(profile, "current_available_balance", 0.0) or 0.0)
    minimum_buffer = float(getattr(profile, "minimum_balance_to_keep", 0.0) or 0.0)

    income = float(state.income or 0.0)
    expenses = float(state.expenses or 0.0)
    essential = float(state.essential_expenses or (expenses * 0.65))
    discretionary = float(state.discretionary_expenses or (expenses * 0.35))
    emi_burden = float(state.emi_burden or 0.0)
    cash_flow = float(state.cash_flow if state.cash_flow is not None else (income - expenses))

    # Determine monthly savings capacity
    if cash_flow > 0:
        monthly_savings = cash_flow
    elif income > 0:
        monthly_savings = max(1000.0, income * 0.15)
    else:
        monthly_savings = 5000.0

    total_90_day_savings = round(monthly_savings * 3, 2)
    projected_end_balance = round(available_balance + total_90_day_savings, 2)

    essential_burn = max(1.0, essential if essential > 0 else (expenses if expenses > 0 else 20000.0))
    runway_months = round(available_balance / essential_burn, 1)

    income_base = max(1.0, income)
    discretionary_ratio_pct = round((discretionary / income_base) * 100, 1)
    savings_rate_pct = round((monthly_savings / income_base) * 100, 1)
    emi_ratio_pct = round((emi_burden / income_base) * 100, 1)

    top_cat_name = "Dining & Discretionary"
    if state.category_spending:
        top_cats = sorted(
            state.category_spending,
            key=lambda c: getattr(c, 'total_amount', getattr(c, 'amount', 0.0)),
            reverse=True
        )
        if top_cats:
            first_cat = top_cats[0].category
            if first_cat and first_cat != "unknown":
                top_cat_name = first_cat.replace('_', ' ').title()

    p1_target = round(monthly_savings, 2)
    p2_target = round(monthly_savings, 2)
    p2_cum = round(monthly_savings * 2, 2)
    p3_target = round(monthly_savings, 2)
    p3_cum = total_90_day_savings

    phase1 = {
        "phase_number": 1,
        "name": "Phase 1: Liquidity & Leakage Plugging",
        "days": "Days 1–30",
        "target_savings": p1_target,
        "cumulative_target": p1_target,
        "focus": "Establish baseline cash discipline, curtail flexible leakage, and automate savings.",
        "advice": [
            f"Set up an automated standing instruction on salary credit day for {currency} {p1_target:,.0f} directly into your reserve account.",
            f"Cap flexible spending in {top_cat_name} by 15–20% to prevent unexpected mid-month cash crunches.",
            "Conduct a zero-delay audit of all active debit mandates and recurring app subscriptions to eliminate unused services."
        ],
        "actions": [
            {"id": "act_1_1", "title": "Automate Salary Day Transfer", "description": f"Schedule auto-deposit of {currency} {p1_target:,.0f} right when income hits.", "completed": False},
            {"id": "act_1_2", "title": f"Curtail {top_cat_name} Leakage", "description": "Set a weekly discretionary card cap to avoid exceeding budget.", "completed": False},
            {"id": "act_1_3", "title": "Audit Recurring Subscriptions", "description": "Identify and cancel unused entertainment or utility memberships.", "completed": False}
        ]
    }

    phase2 = {
        "phase_number": 2,
        "name": "Phase 2: Buffer Fortification & Category Optimization",
        "days": "Days 31–60",
        "target_savings": p2_target,
        "cumulative_target": p2_cum,
        "focus": "Fortify emergency reserve buffer and renegotiate recurring utility/debt costs.",
        "advice": [
            f"Fortify cash balance toward your safety buffer of {currency} {minimum_buffer:,.0f} so unexpected shocks never require high-interest loans.",
            "Compare flexible utility, insurance, and telecom plans to unlock permanent recurring cost reductions.",
            "Review credit card and short-term debt billing cycles to ensure zero interest or penalty accruals."
        ],
        "actions": [
            {"id": "act_2_1", "title": "Reach Halfway Savings Milestone", "description": f"Accumulate cumulative {currency} {p2_cum:,.0f} in liquid buffer.", "completed": False},
            {"id": "act_2_2", "title": "Essential Utility Review", "description": "Optimize electricity, wifi, and grocery spending baskets.", "completed": False},
            {"id": "act_2_3", "title": "Zero-Fee Debt Clearance", "description": "Ensure full payment on credit balances to protect credit score.", "completed": False}
        ]
    }

    phase3 = {
        "phase_number": 3,
        "name": "Phase 3: Resiliency, Compounding & Surplus Allocation",
        "days": "Days 61–90",
        "target_savings": p3_target,
        "cumulative_target": p3_cum,
        "focus": "Lock in compounding resilience and allocate surplus capital beyond buffer.",
        "advice": [
            f"Achieve the full 90-day savings milestone of {currency} {p3_cum:,.0f}, bringing projected liquid balance to {currency} {projected_end_balance:,.0f}.",
            f"Deploy any surplus above the {currency} {minimum_buffer:,.0f} reserve buffer into low-risk liquid yields or short-term deposits.",
            f"Standardize your {savings_rate_pct}% net savings rate as your permanent household operational benchmark."
        ],
        "actions": [
            {"id": "act_3_1", "title": "Complete 90-Day Savings Goal", "description": f"Hit the {currency} {p3_cum:,.0f} cumulative milestone.", "completed": False},
            {"id": "act_3_2", "title": "Deploy Buffer Surplus", "description": "Move funds exceeding emergency reserve into interest-bearing liquid assets.", "completed": False},
            {"id": "act_3_3", "title": "Review 90-Day Run-Rate", "description": "Re-run Artha AI diagnostic to set the subsequent quarter's financial goals.", "completed": False}
        ]
    }

    terms = [
        {
            "term": "Emergency Reserve Buffer (ERB)",
            "key": "erb",
            "your_metric": f"{currency} {minimum_buffer:,.0f}",
            "status": "Healthy" if available_balance >= minimum_buffer else "Needs Fortification",
            "definition": "The non-negotiable cash baseline kept in liquid form to insulate your household against sudden medical emergencies or income shocks.",
            "why_it_matters": "Prevents forced liquidations of long-term investments or recourse to predatory credit when unexpected expenses arise."
        },
        {
            "term": "Liquidity Runway",
            "key": "runway",
            "your_metric": f"{runway_months} Months",
            "status": "Strong" if runway_months >= 3.0 else "Caution",
            "definition": "The exact duration your existing liquid balance can sustain essential baseline expenditures if all income ceased today.",
            "why_it_matters": "A runway of 3 to 6 months provides career resilience, peace of mind, and financial independence."
        },
        {
            "term": "Discretionary Expense Ratio (DER)",
            "key": "der",
            "your_metric": f"{discretionary_ratio_pct}%",
            "status": "Optimal" if discretionary_ratio_pct <= 30 else "High",
            "definition": "The percentage of gross monthly earnings spent on flexible lifestyle choices, dining, entertainment, and non-essential wants.",
            "why_it_matters": "Maintaining DER below 30% guarantees sufficient monthly surplus to feed savings and investment goals."
        },
        {
            "term": "Debt-to-Income / EMI Burden",
            "key": "dti",
            "your_metric": f"{emi_ratio_pct}%",
            "status": "Safe" if emi_ratio_pct <= 35 else "Elevated",
            "definition": "The fraction of monthly earnings committed to fixed debt repayments, loan EMIs, and credit servicing.",
            "why_it_matters": "A low burden (< 35%) ensures high discretionary flexibility and protects against default during income interruptions."
        },
        {
            "term": "Net Savings Yield (Savings Rate)",
            "key": "savings_rate",
            "your_metric": f"{savings_rate_pct}%",
            "status": "High Velocity" if savings_rate_pct >= 25 else "Moderate",
            "definition": "The portion of total monthly income retained as net unspent surplus after meeting all living costs.",
            "why_it_matters": "This single metric dictates how rapidly your net worth compounds and how fast your 90-day roadmap succeeds."
        }
    ]

    return {
        "user_id": str(current_user.id),
        "currency": currency,
        "dataset_summary": {
            "monthly_income": income,
            "monthly_expenses": expenses,
            "monthly_cash_flow": cash_flow,
            "available_balance": available_balance,
            "minimum_buffer": minimum_buffer,
            "essential_expenses": essential,
            "discretionary_expenses": discretionary,
            "emi_burden": emi_burden,
            "liquidity_runway_months": runway_months,
            "savings_rate_pct": savings_rate_pct,
            "discretionary_ratio_pct": discretionary_ratio_pct,
            "emi_ratio_pct": emi_ratio_pct
        },
        "total_90_day_savings_target": total_90_day_savings,
        "projected_end_balance": projected_end_balance,
        "phases": [phase1, phase2, phase3],
        "financial_terms": terms
    }
