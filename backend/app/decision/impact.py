from app.schemas.decision import ScenarioResult, ExpectedImpact

class ImpactEngine:
    """
    Calculates the deterministic expected impact of a scenario compared to a baseline.
    """
    @staticmethod
    def calculate_impact(baseline: ScenarioResult, scenario: ScenarioResult) -> ExpectedImpact:
        cf_diff = scenario.projected_cash_flow - baseline.projected_cash_flow
        bal_diff = scenario.projected_balance - baseline.projected_balance
        
        status_change = "maintained"
        if not baseline.buffer_breached and scenario.buffer_breached:
            status_change = "breached"
        elif baseline.buffer_breached and not scenario.buffer_breached:
            status_change = "restored"
        elif baseline.buffer_breached and scenario.buffer_breached:
            if scenario.shortfall < baseline.shortfall:
                status_change = "improved_but_still_breached"
            elif scenario.shortfall > baseline.shortfall:
                status_change = "worsened_breach"
            else:
                status_change = "still_breached"
                
        return ExpectedImpact(
            cash_flow_difference=cf_diff,
            balance_difference=bal_diff,
            buffer_status_change=status_change
        )
