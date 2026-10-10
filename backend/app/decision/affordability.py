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
    ) -> AffordabilityResult:
        """
        Evaluate whether *amount* is affordable given the user's financial profile
        and projected next-month cash flow.

        Parameters
        ----------
        amount : float
            Proposed one-off purchase price. Must be positive.
        payment_options : list of PaymentOption, optional
            Alternative installment/EMI plans to evaluate.

        Returns
        -------
        AffordabilityResult
            Deterministic result with status, computed balance, shortfall,
            viable payment options, and auditable reasons.
        """
        # -----------------------------------------------------------------
        # Guard: prediction data availability
        # -----------------------------------------------------------------
        if not self.baseline.available:
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

        # -----------------------------------------------------------------
        # Guard: validate proposed amount
        # -----------------------------------------------------------------
        reasons: List[str] = []

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

        baseline_cf = self.baseline.projected_cash_flow

        # -----------------------------------------------------------------
        # Core one-off purchase calculation
        # (modelled as a debit against current balance within this month's cf)
        # -----------------------------------------------------------------
        projected_net_cf = baseline_cf.projected_cash_flow  # income - expenses - obligations
        resulting_balance = self.profile.current_available_balance + projected_net_cf - amount
        shortfall = max(0.0, self.profile.minimum_balance_to_keep - resulting_balance)

        # Build auditable reason strings based on actual values used
        reasons.append(
            f"Current available balance: {self.profile.current_available_balance:.2f}"
        )
        reasons.append(
            f"Projected net cash flow (income {baseline_cf.projected_income:.2f} "
            f"- expenses {baseline_cf.projected_expenses:.2f} "
            f"- obligations {baseline_cf.known_obligations:.2f}): "
            f"{projected_net_cf:.2f}"
        )
        reasons.append(f"Proposed purchase amount: {amount:.2f}")
        reasons.append(f"Resulting balance after purchase: {resulting_balance:.2f}")
        reasons.append(f"Required minimum buffer: {self.profile.minimum_balance_to_keep:.2f}")

        # -----------------------------------------------------------------
        # Status determination
        # -----------------------------------------------------------------
        if resulting_balance >= self.profile.minimum_balance_to_keep:
            status = "AFFORDABLE"
            trade_off = 0.0
            reasons.append(
                f"Result: balance {resulting_balance:.2f} is at or above the minimum buffer "
                f"{self.profile.minimum_balance_to_keep:.2f}."
            )
        elif resulting_balance > 0 and shortfall <= baseline_cf.projected_expenses:
            # Technically possible to cover shortfall from discretionary savings
            status = "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
            trade_off = shortfall
            reasons.append(
                f"Result: balance {resulting_balance:.2f} is below the minimum buffer by {shortfall:.2f}. "
                f"You could cover this shortfall by reducing discretionary spending "
                f"(projected: {baseline_cf.projected_expenses:.2f}) by {shortfall:.2f}."
            )
        else:
            status = "NOT AFFORDABLE UNDER CURRENT PROJECTION"
            trade_off = shortfall
            reasons.append(
                f"Result: balance {resulting_balance:.2f} is below the minimum buffer by {shortfall:.2f}. "
                f"The shortfall ({shortfall:.2f}) exceeds projected discretionary expenses "
                f"({baseline_cf.projected_expenses:.2f}), so a trade-off cannot fully recover it."
            )

        # -----------------------------------------------------------------
        # Payment option viability check
        # (each option is evaluated independently – no double-counting)
        # -----------------------------------------------------------------
        viable_options: List[PaymentOption] = []
        for opt in payment_options:
            if opt.number_of_payments == 1:
                # Full payment — same as the one-off purchase check
                if status in ("AFFORDABLE", "POTENTIALLY AFFORDABLE WITH TRADE-OFF"):
                    viable_options.append(opt)
            elif opt.number_of_payments > 1:
                # Monthly installment — check monthly payment against cf
                monthly_payment = opt.payment_amount
                installment_balance = (
                    self.profile.current_available_balance
                    + projected_net_cf
                    - monthly_payment
                )
                if installment_balance >= self.profile.minimum_balance_to_keep:
                    viable_options.append(opt)

        return AffordabilityResult(
            status=status,
            proposed_expense_amount=amount,
            resulting_balance=resulting_balance,
            shortfall=shortfall,
            viable_payment_options=viable_options,
            trade_off_required=trade_off,
            reasons=reasons,
        )
