from typing import List, Optional
from app.schemas.financial import FinancialProfile, PredictionEngineResult, PaymentOption
from app.schemas.decision import AffordabilityResult


# ---------------------------------------------------------------------------
# Configurable safety threshold
# ---------------------------------------------------------------------------
# Minimum fraction of projected monthly income that must remain as disposable
# cash *after* existing obligations before a purchase is considered affordable.
# Setting to 0.0 means only the profile's minimum_balance_to_keep is enforced.
# Override via subclassing or keyword argument to evaluate_purchase().
DEFAULT_MIN_DISPOSABLE_FRACTION: float = 0.0


class AffordabilityEngine:
    """
    Deterministic affordability evaluator for a proposed purchase or EMI.

    Rules applied (in order)
    -------------------------
    1. If baseline prediction data is unavailable → INSUFFICIENT DATA.
    2. Validate the proposed amount (must be positive).
    3. For a one-off purchase:
       Resulting balance = current_balance + projected_net_cash_flow - purchase_amount
       If resulting_balance >= minimum_balance_to_keep            → AFFORDABLE
       elif resulting_balance > 0 and shortfall <= projected_expenses → POTENTIALLY AFFORDABLE WITH TRADE-OFF
       else                                                        → NOT AFFORDABLE UNDER CURRENT PROJECTION
    4. Payment options are checked independently: each installment's monthly
       impact on the projected balance must keep it >= minimum_balance_to_keep.

    All thresholds are configurable; none are invented without documentation.
    Results are estimates, not guaranteed financial outcomes.
    """

    def __init__(self, profile: FinancialProfile, baseline_prediction: PredictionEngineResult):
        self.profile = profile
        self.baseline = baseline_prediction

    def evaluate_purchase(
        self,
        amount: float,
        payment_options: Optional[List[PaymentOption]] = None,
        stated_balance: Optional[float] = None,
        stated_income: Optional[float] = None,
        stated_expenses: Optional[float] = None,
        stated_buffer: Optional[float] = None,
        is_annual: bool = False,
    ) -> AffordabilityResult:
        """
        Evaluate whether *amount* is affordable given the user's financial profile
        (or explicit stated scenario parameters) and projected cash flow.
        """
        has_stated_scenario = any(v is not None for v in [stated_balance, stated_income, stated_expenses, stated_buffer])
        if not self.baseline.available and not has_stated_scenario:
            return AffordabilityResult(
                status="INSUFFICIENT DATA",
                proposed_expense_amount=amount if amount else 0.0,
                resulting_balance=self.profile.current_available_balance,
                shortfall=0.0,
                reasons=[
                    "Insufficient historical transaction data (minimum 3 months required). "
                    "Cannot project cash flow."
                ],
            )

        if amount is None or amount <= 0:
            return AffordabilityResult(
                status="INSUFFICIENT DATA",
                proposed_expense_amount=amount if amount is not None else 0.0,
                resulting_balance=self.profile.current_available_balance,
                shortfall=0.0,
                reasons=["Proposed purchase amount must be greater than zero."],
            )

        if payment_options is None:
            payment_options = []

        baseline_cf = self.baseline.projected_cash_flow if (self.baseline.available and self.baseline.projected_cash_flow) else None

        data_sources: dict = {}
        conflicts: List[str] = []

        # 1. Resolve Active Balance
        if stated_balance is not None:
            active_balance = float(stated_balance)
            data_sources["current_balance"] = "Stated Scenario Override"
            if abs(active_balance - self.profile.current_available_balance) > 0.01:
                conflicts.append(
                    f"Stated bank balance ({active_balance:,.2f}) differs from profile on record ({self.profile.current_available_balance:,.2f})"
                )
        else:
            active_balance = float(self.profile.current_available_balance)
            data_sources["current_balance"] = "Profile on Record"

        # 2. Resolve Active Buffer / Emergency Fund
        if stated_buffer is not None:
            active_buffer = float(stated_buffer)
            data_sources["minimum_buffer"] = "Stated Emergency Fund Target"
            if abs(active_buffer - self.profile.minimum_balance_to_keep) > 0.01:
                conflicts.append(
                    f"Stated minimum emergency fund ({active_buffer:,.2f}) differs from profile reserve ({self.profile.minimum_balance_to_keep:,.2f})"
                )
        else:
            active_buffer = float(self.profile.minimum_balance_to_keep)
            data_sources["minimum_buffer"] = "Profile on Record"

        # 3. Resolve Active Monthly Income
        if stated_income is not None:
            active_income = float(stated_income)
            data_sources["monthly_income"] = "Stated Scenario Input"
            if baseline_cf and abs(active_income - baseline_cf.projected_income) > 0.01:
                conflicts.append(
                    f"Stated monthly income ({active_income:,.2f}) differs from historical forecast ({baseline_cf.projected_income:,.2f})"
                )
        elif baseline_cf:
            active_income = float(baseline_cf.projected_income)
            data_sources["monthly_income"] = "Baseline ML Forecast"
        else:
            active_income = 0.0
            data_sources["monthly_income"] = "Not Available"

        # 4. Resolve Active Monthly Expenses
        if stated_expenses is not None:
            active_expenses = float(stated_expenses)
            data_sources["monthly_expenses"] = "Stated Scenario Input"
            if baseline_cf and abs(active_expenses - baseline_cf.projected_expenses) > 0.01:
                conflicts.append(
                    f"Stated monthly expenses ({active_expenses:,.2f}) differs from historical forecast ({baseline_cf.projected_expenses:,.2f})"
                )
        elif baseline_cf:
            active_expenses = float(baseline_cf.projected_expenses)
            data_sources["monthly_expenses"] = "Baseline ML Forecast"
        else:
            active_expenses = 0.0
            data_sources["monthly_expenses"] = "Not Available"

        known_obligations = float(baseline_cf.known_obligations) if baseline_cf else 0.0

        # 5. Core Financial Calculations
        monthly_savings = round(active_income - active_expenses, 2)
        data_sources["monthly_savings"] = "Calculated (Monthly Income - Monthly Expenses)"

        if is_annual:
            monthly_premium_provision = round(amount / 12.0, 2)
            data_sources["monthly_premium_provision"] = "Calculated (Annual Premium / 12)"
        else:
            monthly_premium_provision = None

        immediate_post_payment_balance = round(active_balance - amount, 2)
        data_sources["immediate_post_payment_balance"] = "Calculated (Bank Balance - Purchase Amount)"

        balance_above_emergency_fund = round(immediate_post_payment_balance - active_buffer, 2)
        data_sources["balance_above_emergency_fund"] = "Calculated (Immediate Post-Payment Balance - Minimum Emergency Fund)"

        projected_net_cf = round(monthly_savings - known_obligations, 2)
        data_sources["projected_net_cash_flow"] = "Calculated (Net Monthly Savings - Obligations)"

        resulting_balance = round(active_balance + projected_net_cf - amount, 2)
        shortfall = max(0.0, round(active_buffer - resulting_balance, 2))
        has_conflict = len(conflicts) > 0

        # 6. Status Determination
        reasons: List[str] = [
            f"Bank balance: {active_balance:,.2f} ({data_sources['current_balance']})",
            f"Monthly income: {active_income:,.2f} ({data_sources['monthly_income']})",
            f"Monthly expenses: {active_expenses:,.2f} ({data_sources['monthly_expenses']})",
            f"Monthly savings: {monthly_savings:,.2f} (Calculated: Income - Expenses)",
            f"Purchase/Premium amount: {amount:,.2f}" + (" (Annual Premium)" if is_annual else ""),
        ]
        if is_annual and monthly_premium_provision is not None:
            reasons.append(f"Monthly premium provision: {monthly_premium_provision:,.2f} (Annual Premium ÷ 12)")
        reasons.append(f"Immediate post-payment balance: {immediate_post_payment_balance:,.2f} (Balance - Purchase Amount)")
        reasons.append(f"Minimum emergency fund: {active_buffer:,.2f} ({data_sources['minimum_buffer']})")
        reasons.append(f"Balance above emergency fund: {balance_above_emergency_fund:,.2f} (Post-Payment Balance - Emergency Fund)")
        reasons.append(f"Projected net cash flow: {projected_net_cf:,.2f}")
        reasons.append(f"Resulting balance after cycle: {resulting_balance:,.2f}")
        if conflicts:
            reasons.append(f"Input conflicts vs saved profile: {'; '.join(conflicts)}")

        if resulting_balance >= active_buffer and immediate_post_payment_balance >= active_buffer:
            status = "AFFORDABLE"
            trade_off = 0.0
            reasons.append(
                f"Result: immediate balance ({immediate_post_payment_balance:,.2f}) and resulting balance ({resulting_balance:,.2f}) "
                f"both maintain the required buffer ({active_buffer:,.2f})."
            )
        elif resulting_balance >= active_buffer and immediate_post_payment_balance < active_buffer:
            # Temporary buffer dip until month-end cash flow covers it
            status = "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
            trade_off = max(0.0, active_buffer - immediate_post_payment_balance)
            reasons.append(
                f"Result: immediate payment temporarily draws balance to {immediate_post_payment_balance:,.2f} "
                f"(below buffer {active_buffer:,.2f} by {trade_off:,.2f}), restored by month-end cash flow."
            )
        elif resulting_balance > 0 and shortfall <= (active_expenses if active_expenses > 0 else 1.0):
            status = "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
            trade_off = shortfall
            reasons.append(
                f"Result: resulting balance {resulting_balance:,.2f} is below minimum buffer by {shortfall:,.2f}. "
                f"You could cover this shortfall by reducing discretionary spending."
            )
        else:
            status = "NOT AFFORDABLE UNDER CURRENT PROJECTION"
            trade_off = shortfall
            reasons.append(
                f"Result: resulting balance {resulting_balance:,.2f} breaches minimum buffer by {shortfall:,.2f}."
            )

        # 7. Payment Option Viability Check
        viable_options: List[PaymentOption] = []
        for opt in payment_options:
            if opt.number_of_payments == 1:
                if status in ("AFFORDABLE", "POTENTIALLY AFFORDABLE WITH TRADE-OFF"):
                    viable_options.append(opt)
            elif opt.number_of_payments > 1:
                monthly_payment = opt.payment_amount
                installment_balance = active_balance + projected_net_cf - monthly_payment
                if installment_balance >= active_buffer:
                    viable_options.append(opt)

        return AffordabilityResult(
            status=status,
            proposed_expense_amount=amount,
            resulting_balance=resulting_balance,
            shortfall=shortfall,
            viable_payment_options=viable_options,
            trade_off_required=trade_off,
            reasons=reasons,
            immediate_post_payment_balance=immediate_post_payment_balance,
            balance_above_emergency_fund=balance_above_emergency_fund,
            monthly_savings=monthly_savings,
            monthly_premium_provision=monthly_premium_provision,
            is_annual_premium=is_annual,
            has_conflict=has_conflict,
            data_sources=data_sources,
        )
