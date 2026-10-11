import re
from typing import Set, List, Dict, Any, Tuple
from app.artha_ai.schemas import ArthaFinancialContextContract, ValidationResult, CalculationStatus


class ArthaResponseValidator:
    """
    Deterministic validation and grounding gatekeeper.
    Ensures that any numerical figures in the LLM explanation
    are grounded in authorized backend calculation results.
    """

    ALLOWED_GENERIC_INTEGERS = {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 18, 21, 24, 30, 36, 48, 60, 100
    }

    @classmethod
    def extract_authorized_numbers(cls, context: ArthaFinancialContextContract) -> Set[float]:
        """Collect all authoritative numerical values from the context."""
        authorized: Set[float] = set()

        def _add_num(v):
            if isinstance(v, (int, float)):
                authorized.add(round(float(v), 2))
                authorized.add(round(abs(float(v)), 2))
                # Also add integer representation
                authorized.add(round(float(int(v)), 2))

        # 1. Calculated results
        for k, v in context.calculated_results.items():
            if isinstance(v, (int, float)):
                _add_num(v)
            elif isinstance(v, list) and k == "viable_options":
                for opt in v:
                    _add_num(opt.get("payment_amount"))
                    _add_num(opt.get("total_payable_amount"))
                    _add_num(opt.get("number_of_payments"))
                    _add_num(opt.get("financing_fee"))
            elif isinstance(v, list) and k == "top_categories":
                for cat in v:
                    _add_num(cat.get("amount"))

        # 2. Forecast
        if context.forecast:
            fc = context.forecast
            _add_num(fc.projected_income)
            _add_num(fc.projected_expenses)
            _add_num(fc.known_obligations)
            _add_num(fc.projected_cash_flow)
            _add_num(fc.projected_balance)

        # 3. Scenario
        if context.scenario_results:
            sc = context.scenario_results
            _add_num(sc.change_amount)
            _add_num(sc.baseline_balance)
            _add_num(sc.scenario_balance)
            _add_num(sc.cash_flow_difference)

        # 4. Financial evidence
        for ev in context.financial_evidence:
            _add_num(ev.amount)

        return authorized

    @classmethod
    def extract_claimed_numbers(cls, text: str) -> List[Tuple[float, str]]:
        """
        Extract numerical tokens from text, removing commas and currency symbols.
        Returns tuples of (parsed_float, raw_token).

        Pre-processes comma-formatted numbers (e.g. 1,302.40 or 11,000) into
        their plain numeric form before matching, preventing split-token false
        positives such as 1302 -> (130, 2).
        """
        # Step 1: Normalize comma-formatted numbers in the text BEFORE regex matching.
        # Matches patterns like 1,302.40 or 1,02,500 or 11,000 and collapses commas.
        normalized = re.sub(
            r"\b(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?)\b",
            lambda m: m.group(0).replace(",", ""),
            text
        )

        # Step 2: Extract all numeric tokens from the normalized text.
        raw_matches = re.findall(
            r"(?:[\$€₹]|(?:INR|USD|EUR)\s*)?(\d+(?:\.\d+)?)",
            normalized
        )
        claimed: List[Tuple[float, str]] = []

        for m in raw_matches:
            try:
                val = float(m)
                claimed.append((val, m))
            except ValueError:
                pass

        return claimed

    @classmethod
    def validate(
        cls,
        response_text: str,
        context: ArthaFinancialContextContract
    ) -> ValidationResult:
        """
        Run deterministic grounding verification on generated text.
        """
        error_reasons: List[str] = []
        unsupported: List[float] = []
        currency_mismatches: List[str] = []

        # 1. Check for insufficient data compliance
        if context.calculation_status == CalculationStatus.INSUFFICIENT_DATA:
            # Response must communicate uncertainty/insufficient data
            lower_text = response_text.lower()
            if not any(phrase in lower_text for phrase in ["not enough", "insufficient", "history", "unavailable", "data"]):
                error_reasons.append(
                    "Context indicates INSUFFICIENT_DATA, but response does not disclose lack of historical data."
                )

        # 2. Currency check
        expected_currency = context.currency.upper()
        if expected_currency == "INR":
            # Disallow hallucinated $ or € unless explicitly in context
            if "$" in response_text:
                currency_mismatches.append("Found '$' symbol when expected home currency is INR (₹).")
            if "€" in response_text:
                currency_mismatches.append("Found '€' symbol when expected home currency is INR (₹).")

        # 3. Grounding check on claimed numbers
        authorized_numbers = cls.extract_authorized_numbers(context)
        claimed_numbers = cls.extract_claimed_numbers(response_text)
        detected_vals: List[float] = []

        for val, raw in claimed_numbers:
            detected_vals.append(val)
            # Allow common integers (e.g. counts, months: 1..24, 100%)
            if val in cls.ALLOWED_GENERIC_INTEGERS or (val.is_integer() and int(val) in cls.ALLOWED_GENERIC_INTEGERS):
                continue

            # Check if within tolerance of any authorized number
            is_grounded = any(
                abs(val - auth) < 0.1 or (auth > 0 and abs(val - auth) / auth < 0.01)
                for auth in authorized_numbers
            )

            if not is_grounded:
                unsupported.append(val)
                error_reasons.append(f"Claimed number '{raw}' ({val}) is not present in authorized backend results.")

        is_valid = len(error_reasons) == 0 and len(currency_mismatches) == 0

        return ValidationResult(
            is_valid=is_valid,
            detected_numbers=detected_vals,
            unsupported_numbers=unsupported,
            currency_mismatches=currency_mismatches,
            error_reasons=error_reasons,
            repaired=False
        )
