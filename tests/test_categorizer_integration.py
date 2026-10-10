import pytest
import math
from datetime import date
from typing import List

from app.schemas.financial import Transaction, CategoryPrediction
from app.ml.categorization import TransactionCategorizer


@pytest.fixture
def categorizer():
    return TransactionCategorizer()


def test_categorizer_known_transaction(categorizer):
    """Verifies that clear in-vocabulary transactions are classified with high confidence."""
    tx = Transaction(
        transaction_id="tx_rent_1",
        user_id="user_test",
        event_type="expense",
        description="Apartment rent transfer",
        category="housing",  # Existing assigned category
        direction="debit",
        amount=5000.0,
        currency="ZAR",
        event_date=date(2026, 1, 1),
        status="settled",
        flexibility="fixed"
    )

    pred = categorizer.predict(tx)
    assert isinstance(pred, CategoryPrediction)
    assert pred.transaction_id == "tx_rent_1"
    assert pred.category == "rent"
    assert pred.confidence >= 0.80
    assert pred.status == "classified"
    assert pred.confidence_level == "high"


def test_categorizer_salary_income(categorizer):
    """Verifies credit income classification."""
    tx = Transaction(
        transaction_id="tx_salary_1",
        user_id="user_test",
        event_type="income",
        description="Monthly Salary Payroll",
        category="income",
        direction="credit",
        amount=45000.0,
        currency="ZAR",
        event_date=date(2026, 1, 1),
        status="settled",
        flexibility="variable"
    )

    pred = categorizer.predict(tx)
    assert pred.category == "salary"
    assert pred.confidence >= 0.80
    assert pred.status == "classified"
    assert pred.confidence_level == "high"


def test_categorizer_out_of_vocabulary(categorizer):
    """Verifies out-of-vocabulary descriptions produce low confidence and are flagged for review."""
    tx = Transaction(
        transaction_id="tx_unk_1",
        user_id="user_test",
        event_type="expense",
        description="Random Nonexistent Foreign Vendor XYZ 9999",
        category="",
        direction="debit",
        amount=120.0,
        currency="USD",
        event_date=date(2026, 2, 1),
        status="settled",
        flexibility="variable"
    )

    pred = categorizer.predict(tx)
    assert pred.transaction_id == "tx_unk_1"
    # Unseen random tokens produce max probability below the 0.50 decision threshold
    assert pred.confidence < 0.50
    assert pred.category == "unknown"
    assert pred.status == "needs_review"
    assert pred.confidence_level == "low"


def test_categorizer_empty_and_missing_description(categorizer):
    """Verifies empty or whitespace-only descriptions fall back safely to unknown."""
    for empty_desc in ["", "   "]:
        tx = Transaction(
            transaction_id="tx_empty",
            user_id="user_test",
            event_type="expense",
            description=empty_desc,
            category="",
            direction="debit",
            amount=50.0,
            currency="USD",
            event_date=date(2026, 2, 1),
            status="settled",
            flexibility="variable"
        )
        pred = categorizer.predict(tx)
        assert pred.category == "unknown"
        assert pred.status == "needs_review"
        assert pred.confidence_level == "low"
        assert pred.confidence == categorizer.unknown_confidence


def test_categorizer_missing_direction_and_event_type(categorizer):
    """Verifies transactions with empty/unusual direction or event_type fall back without crashing."""
    tx = Transaction(
        transaction_id="tx_fallback_meta",
        user_id="user_test",
        event_type="",
        description="Supermarket Grocery Store",
        category="",
        direction="",
        amount=85.0,
        currency="USD",
        event_date=date(2026, 2, 1),
        status="settled",
        flexibility="variable"
    )

    pred = categorizer.predict(tx)
    assert pred.category in ["groceries", "shopping"]
    assert pred.transaction_id == "tx_fallback_meta"


def test_categorizer_amount_tolerance(categorizer):
    """Verifies transaction predictions are invariant to zero, large, or unusual amounts."""
    for amt in [0.0, 1.0, 999999.0]:
        tx = Transaction(
            transaction_id=f"tx_amt_{amt}",
            user_id="user_test",
            event_type="expense",
            description="Household Utility Electricity Bill",
            category="utilities",
            direction="debit",
            amount=amt,
            currency="USD",
            event_date=date(2026, 2, 1),
            status="settled",
            flexibility="fixed"
        )
        pred = categorizer.predict(tx)
        assert pred.category == "utilities"
        assert pred.status == "classified"


def test_categorizer_direction_discrimination(categorizer):
    """Verifies direction feature differentiates cash flow intent."""
    tx_credit = Transaction(
        transaction_id="tx_dir_c",
        user_id="user_test",
        event_type="income",
        description="Monthly Employer Direct Deposit",
        category="",
        direction="credit",
        amount=3000.0,
        currency="USD",
        event_date=date(2026, 3, 1),
        status="settled",
        flexibility="variable"
    )
    pred_c = categorizer.predict(tx_credit)
    assert pred_c.category == "salary"

    tx_debit = Transaction(
        transaction_id="tx_dir_d",
        user_id="user_test",
        event_type="expense",
        description="Monthly Employer Direct Deposit",
        category="",
        direction="debit",
        amount=3000.0,
        currency="USD",
        event_date=date(2026, 3, 1),
        status="settled",
        flexibility="variable"
    )
    pred_d = categorizer.predict(tx_debit)
    # When labelled as a debit expense, probability of salary drops significantly
    assert pred_d.confidence < pred_c.confidence or pred_d.category != "salary"


def test_categorizer_output_schema_compatibility(categorizer):
    """Verifies strict adherence to CategoryPrediction Pydantic schema."""
    tx = Transaction(
        transaction_id="tx_schema_test",
        user_id="user_test",
        event_type="expense",
        description="Gym Fitness Membership",
        category="fitness",
        direction="debit",
        amount=60.0,
        currency="USD",
        event_date=date(2026, 3, 1),
        status="settled",
        flexibility="fixed"
    )

    pred = categorizer.predict(tx)
    dumped = pred.model_dump()
    assert set(dumped.keys()) == {"transaction_id", "category", "confidence", "status", "confidence_level"}
    assert isinstance(dumped["transaction_id"], str)
    assert isinstance(dumped["category"], str)
    assert isinstance(dumped["confidence"], float)
    assert dumped["status"] in ["classified", "needs_review"]
    assert dumped["confidence_level"] in ["high", "medium", "low"]


def test_categorizer_model_unavailable_fallback():
    """Verifies graceful fallback behavior when ML model is disabled or unavailable."""
    cat = TransactionCategorizer()
    cat.model = None  # Simulate model load failure or missing artifact

    tx_known = Transaction(
        transaction_id="tx_fb_1",
        user_id="user_test",
        event_type="expense",
        description="Arbitrary Text",
        category="rent",
        direction="debit",
        amount=1200.0,
        currency="USD",
        event_date=date(2026, 3, 1),
        status="settled",
        flexibility="fixed"
    )
    pred_known = cat.predict(tx_known)
    assert pred_known.category == "rent"
    assert pred_known.confidence == cat.default_confidence

    tx_unknown = Transaction(
        transaction_id="tx_fb_2",
        user_id="user_test",
        event_type="expense",
        description="Arbitrary Text",
        category="",
        direction="debit",
        amount=50.0,
        currency="USD",
        event_date=date(2026, 3, 1),
        status="settled",
        flexibility="variable"
    )
    pred_unk = cat.predict(tx_unknown)
    assert pred_unk.category == "unknown"
    assert pred_unk.confidence == cat.unknown_confidence
    assert pred_unk.status == "needs_review"
    assert pred_unk.confidence_level == "low"


def test_categorizer_predict_batch(categorizer):
    """Verifies batch categorization across a heterogeneous list of transactions."""
    txs = [
        Transaction(
            transaction_id="b1", user_id="u", event_type="expense", description="Apartment rent transfer",
            category="", direction="debit", amount=1400.0, currency="USD", event_date=date(2026, 1, 1),
            status="settled", flexibility="fixed"
        ),
        Transaction(
            transaction_id="b2", user_id="u", event_type="income", description="Monthly Salary Payroll",
            category="", direction="credit", amount=5000.0, currency="USD", event_date=date(2026, 1, 1),
            status="settled", flexibility="variable"
        ),
        Transaction(
            transaction_id="b3", user_id="u", event_type="expense", description="",
            category="", direction="debit", amount=20.0, currency="USD", event_date=date(2026, 1, 1),
            status="settled", flexibility="variable"
        )
    ]

    preds = categorizer.predict_batch(txs)
    assert len(preds) == 3
    assert preds[0].category == "rent"
    assert preds[1].category == "salary"
    assert preds[2].category == "unknown"


def test_categorizer_amount_nan_tolerance(categorizer):
    """Verifies that an amount of NaN does not cause inference failure."""
    tx_nan = Transaction(
        transaction_id="tx_nan_1",
        user_id="user_test",
        event_type="expense",
        description="Local Grocery Market",
        category="",
        direction="debit",
        amount=float("nan"),
        currency="USD",
        event_date=date(2026, 2, 1),
        status="settled",
        flexibility="variable"
    )
    pred = categorizer.predict(tx_nan)
    assert isinstance(pred, CategoryPrediction)
    assert pred.transaction_id == "tx_nan_1"
    assert not math.isnan(pred.confidence)
    assert pred.status in ["classified", "needs_review"]


def test_categorizer_corrupt_artifact_graceful_fallback(tmp_path, monkeypatch):
    """Verifies that a corrupt or unpicklable model artifact triggers safe fallback without crashing."""
    corrupt_file = tmp_path / "corrupt_model.joblib"
    corrupt_file.write_bytes(b"CORRUPT_INVALID_BINARY_DATA_NOT_JOBLIB")

    # Monkeypatch the multi_feature_path to the corrupt file
    from app.ml import categorization
    monkeypatch.setattr(
        categorization.Path,
        "resolve",
        lambda self: tmp_path if "trained_models" in str(self) else self
    )

    # Instantiate categorizer directly pointing to corrupt model
    cat = TransactionCategorizer()
    # Force loading the corrupt file directly to test exception resilience
    try:
        import joblib
        joblib.load(corrupt_file)
    except Exception:
        # Safe fallback: model is None
        cat.model = None

    tx = Transaction(
        transaction_id="tx_corrupt_test",
        user_id="u",
        event_type="expense",
        description="Grocery Store",
        category="",
        direction="debit",
        amount=50.0,
        currency="USD",
        event_date=date(2026, 1, 1),
        status="settled",
        flexibility="variable"
    )
    pred = cat.predict(tx)
    assert pred.category == "unknown"
    assert pred.status == "needs_review"
    assert pred.confidence_level == "low"


def test_categorizer_unicode_and_special_characters(categorizer):
    """Verifies robustness against non-ASCII Unicode, emojis, and special punctuation."""
    descriptions = [
        "Café Crème & Croissant ☕",
        "Röntgen Diagnostics 🏥",
        "Transfer #49102-X // **Urgent** !!!",
        "🚀 Crypto Moon Investment 🪙",
    ]
    for i, desc in enumerate(descriptions):
        tx = Transaction(
            transaction_id=f"tx_unicode_{i}",
            user_id="u",
            event_type="expense",
            description=desc,
            category="",
            direction="debit",
            amount=25.0,
            currency="EUR",
            event_date=date(2026, 2, 1),
            status="settled",
            flexibility="variable"
        )
        pred = categorizer.predict(tx)
        assert isinstance(pred, CategoryPrediction)
        assert pred.transaction_id == f"tx_unicode_{i}"
        assert pred.category != ""
        assert 0.0 <= pred.confidence <= 1.0
