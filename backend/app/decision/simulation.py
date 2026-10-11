from typing import Optional
from app.schemas.financial import FinancialProfile, PredictionEngineResult
from app.schemas.decision import ScenarioResult, WhatIfSummary


class WhatIfSimulator:
    """
    Deterministic What-If Simulation Engine.

    Creates scenario results by applying deterministic adjustments to the
    baseline PredictionEngineResult. All monetary amounts are monthly figures.

    Supported scenario types
    ------------------------
    * reduce_discretionary_spending – monthly expense *decreases* by a positive amount
    * increase_spending              – monthly expense *increases* by a positive amount
    * add_obligation                 – a new recurring monthly obligation added
    * reduce_discretionary_pct      – expense reduced by a fraction of current expenses
    """

    def __init__(self, profile: FinancialProfile, baseline_prediction: PredictionEngineResult):
        self.profile = profile
        self.baseline = baseline_prediction

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_baseline_cash_flow(self):
        return self.baseline.projected_cash_flow

    def _calculate_scenario(
        self,
        name: str,
        adj_income: float,
        adj_expenses: float,
        adj_obligations: float,
    ) -> ScenarioResult:
        """
        Compute one month's scenario result from signed adjustments.

        Positive adj_expenses means *more* spending; negative means *less* spending.
        """
        baseline_cf = self._get_baseline_cash_flow()

        new_income = max(0.0, baseline_cf.projected_income + adj_income)
        new_expenses = max(0.0, baseline_cf.projected_expenses + adj_expenses)
        new_obligations = max(0.0, baseline_cf.known_obligations + adj_obligations)

        new_cash_flow = new_income - new_expenses - new_obligations
        new_balance = self.profile.current_available_balance + new_cash_flow

        shortfall = max(0.0, self.profile.minimum_balance_to_keep - new_balance)
        buffer_breached = shortfall > 0

        return ScenarioResult(
            scenario_name=name,
            projected_income=new_income,
            projected_expenses=new_expenses,
            known_obligations=new_obligations,
            projected_cash_flow=new_cash_flow,
            projected_balance=new_balance,
            shortfall=shortfall,
            buffer_breached=buffer_breached,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def baseline_scenario(self) -> ScenarioResult:
        if not self.baseline.available:
            raise ValueError("Baseline prediction is not available.")
        return self._calculate_scenario("Baseline", 0.0, 0.0, 0.0)

    def simulate_reduce_discretionary_spending(self, reduction_amount: float) -> ScenarioResult:
        """
        Simulate reducing monthly discretionary expenses by *reduction_amount*.

        Parameters
        ----------
        reduction_amount : float
            Positive value representing how much less is spent each month.

        Raises
        ------
        ValueError
            If reduction_amount is negative or zero.
        """
        if not self.baseline.available:
            raise ValueError("Baseline prediction is not available.")
        if reduction_amount < 0:
            raise ValueError(
                "reduction_amount must be non-negative. "
                "To model an increase use simulate_increase_spending()."
            )
        if reduction_amount == 0:
            return self.baseline_scenario()
        return self._calculate_scenario(
            f"Reduce Discretionary by {reduction_amount:.2f}",
            0.0,
            -reduction_amount,  # negative adj → fewer expenses
            0.0,
        )

    def simulate_increase_spending(self, increase_amount: float) -> ScenarioResult:
        """
        Simulate increasing monthly discretionary expenses by *increase_amount*.

        Parameters
        ----------
        increase_amount : float
            Positive value representing how much more is spent each month.

        Raises
        ------
        ValueError
            If increase_amount is negative or zero.
        """
        if not self.baseline.available:
            raise ValueError("Baseline prediction is not available.")
        if increase_amount < 0:
            raise ValueError(
                "increase_amount must be non-negative. "
                "To model a reduction use simulate_reduce_discretionary_spending()."
            )
        if increase_amount == 0:
            return self.baseline_scenario()
        return self._calculate_scenario(
            f"Increase Spending by {increase_amount:.2f}",
            0.0,
            +increase_amount,  # positive adj → more expenses
            0.0,
        )

    def simulate_add_obligation(self, amount: float) -> ScenarioResult:
        """Add a new monthly obligation (e.g. a new EMI)."""
        if not self.baseline.available:
            raise ValueError("Baseline prediction is not available.")
        if amount < 0:
            raise ValueError("Obligation amount must be non-negative.")
        return self._calculate_scenario(f"Add Obligation of {amount:.2f}", 0.0, 0.0, amount)

    def simulate_reduce_income(self, reduction_amount: float) -> ScenarioResult:
        """Simulate reducing monthly income by reduction_amount."""
        if not self.baseline.available:
            raise ValueError("Baseline prediction is not available.")
        if reduction_amount < 0:
            raise ValueError("reduction_amount must be non-negative.")
        if reduction_amount == 0:
            return self.baseline_scenario()
        return self._calculate_scenario(
            f"Reduce Income by {reduction_amount:.2f}",
            -reduction_amount,  # negative adj -> less income
            0.0,
            0.0,
        )

    def simulate_reduce_discretionary_percentage(self, percentage: float) -> ScenarioResult:
        """Reduce expenses by *percentage* of current projected expenses (0–1)."""
        if not self.baseline.available:
            raise ValueError("Baseline prediction is not available.")
        if percentage < 0 or percentage > 1:
            raise ValueError("Percentage must be between 0 and 1.")
        current_expenses = self._get_baseline_cash_flow().projected_expenses
        reduction_amount = current_expenses * percentage
        return self._calculate_scenario(
            f"Reduce Discretionary by {percentage * 100:.1f}%",
            0.0,
            -reduction_amount,
            0.0,
        )

    # ------------------------------------------------------------------
    # Multi-month cumulative summary
    # ------------------------------------------------------------------

    def compute_what_if_summary(
        self,
        baseline: ScenarioResult,
        scenario: ScenarioResult,
        months: int = 6,
    ) -> WhatIfSummary:
        """
        Build a deterministic, multi-month summary comparing baseline vs. scenario.

        Parameters
        ----------
        baseline : ScenarioResult
        scenario : ScenarioResult
        months   : int  Number of months to project (default 6).

        Returns
        -------
        WhatIfSummary
            Monthly differences and a cumulative total over the forecast horizon.
        """
        if months < 1:
            raise ValueError("months must be at least 1.")

        monthly_cf_diff = scenario.projected_cash_flow - baseline.projected_cash_flow
        monthly_balance_diff = scenario.projected_balance - baseline.projected_balance
        cumulative_cf_diff = monthly_cf_diff * months
        cumulative_balance_diff = monthly_balance_diff * months

        return WhatIfSummary(
            baseline_monthly_income=baseline.projected_income,
            baseline_monthly_expenses=baseline.projected_expenses,
            baseline_monthly_cash_flow=baseline.projected_cash_flow,
            scenario_monthly_income=scenario.projected_income,
            scenario_monthly_expenses=scenario.projected_expenses,
            scenario_monthly_cash_flow=scenario.projected_cash_flow,
            monthly_cash_flow_difference=monthly_cf_diff,
            monthly_balance_difference=monthly_balance_diff,
            cumulative_cash_flow_difference=cumulative_cf_diff,
            cumulative_balance_difference=cumulative_balance_diff,
            forecast_months=months,
        )
