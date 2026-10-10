from typing import List
from app.schemas.financial import FinancialProfile, PredictionEngineResult, PaymentOption
from app.schemas.decision import AffordabilityResult

class AffordabilityEngine:
    """
    Deterministic affordability and scenario function to evaluate a proposed expense.
    """
    def __init__(self, profile: FinancialProfile, baseline_prediction: PredictionEngineResult):
        self.profile = profile
        self.baseline = baseline_prediction

    def evaluate_purchase(self, amount: float, payment_options: List[PaymentOption] = None) -> AffordabilityResult:
        if not self.baseline.available:
            return AffordabilityResult(
                status="INSUFFICIENT DATA",
                proposed_expense_amount=amount,
                resulting_balance=self.profile.current_available_balance,
                shortfall=0.0,
                trade_off_required=0.0
            )

        if payment_options is None:
            payment_options = []

        baseline_cf = self.baseline.projected_cash_flow
        
        # Calculate resulting balance after immediate full payment
        # Since this is a one-off purchase, it hits the balance immediately or hits this month's cash flow.
        # We model it as a reduction in current balance for the month.
        resulting_balance = self.profile.current_available_balance + baseline_cf.projected_cash_flow - amount
        shortfall = max(0.0, self.profile.minimum_balance_to_keep - resulting_balance)

        if resulting_balance >= self.profile.minimum_balance_to_keep:
            status = "AFFORDABLE"
            trade_off = 0.0
        elif resulting_balance > 0 and shortfall <= baseline_cf.projected_expenses:
            # We can afford it IF we reduce discretionary expenses (trade-off)
            status = "POTENTIALLY AFFORDABLE WITH TRADE-OFF"
            trade_off = shortfall
        else:
            status = "NOT AFFORDABLE UNDER CURRENT PROJECTION"
            trade_off = shortfall

        # Filter viable payment options based on monthly cash flow if installment
        viable_options = []
        for opt in payment_options:
            if opt.number_of_payments == 1:
                if status in ["AFFORDABLE", "POTENTIALLY AFFORDABLE WITH TRADE-OFF"]:
                    viable_options.append(opt)
            elif opt.number_of_payments > 1:
                # Can we afford the monthly installment?
                monthly_installment = opt.payment_amount
                installment_resulting_balance = self.profile.current_available_balance + baseline_cf.projected_cash_flow - monthly_installment
                if installment_resulting_balance >= self.profile.minimum_balance_to_keep:
                    viable_options.append(opt)

        return AffordabilityResult(
            status=status,
            proposed_expense_amount=amount,
            resulting_balance=resulting_balance,
            shortfall=shortfall,
            viable_payment_options=viable_options,
            trade_off_required=trade_off
        )
