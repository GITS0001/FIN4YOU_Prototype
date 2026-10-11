import pytest
from datetime import date
from app.financial.merchants import (
    detect_merchant_info,
    resolve_category_from_description,
    extract_merchant_breakdown,
)
from app.ml.categorization import TransactionCategorizer
from app.financial.state import FinancialStateEngine
from app.schemas.financial import Transaction, FinancialProfile
from app.copilot.intent_parser import IntentParser
from app.schemas.copilot import IntentType
from app.copilot.tools import execute_spending_analysis, SpendingAnalysisArgs
from app.copilot.response_generator import ResponseGenerator


def test_merchant_detection():
    # Shopping
    m_myntra = detect_merchant_info("UPI/MYNTRA DESIGNS/ORDER123")
    assert m_myntra is not None
    assert m_myntra["category"] == "shopping"
    assert m_myntra["display_name"] == "Myntra"

    m_amazon = detect_merchant_info("AMAZON PAY INDIA PVT LTD")
    assert m_amazon is not None
    assert m_amazon["category"] == "shopping"
    assert m_amazon["display_name"] == "Amazon"

    # Food
    m_swiggy = detect_merchant_info("SWIGGY BANGALORE IN")
    assert m_swiggy is not None
    assert m_swiggy["category"] == "food"
    assert m_swiggy["display_name"] == "Swiggy"

    m_blinkit = detect_merchant_info("BLINKIT COMMERCE GURGAON")
    assert m_blinkit is not None
    assert m_blinkit["category"] == "food"
    assert m_blinkit["display_name"] == "Blinkit"

    # Travel
    m_uber = detect_merchant_info("UBER INDIA RIDES BV")
    assert m_uber is not None
    assert m_uber["category"] == "travel"
    assert m_uber["display_name"] == "Uber"


def test_ml_categorizer_uses_merchants():
    categorizer = TransactionCategorizer()
    t1 = Transaction(
        transaction_id="1", user_id="u1", description="Payment to Myntra Fashion",
        amount=2000.0, currency="INR", direction="debit", status="COMPLETED",
        category="unknown", event_type="expense", event_date=date.today(), flexibility="variable"
    )
    assert categorizer.predict(t1).category == "shopping"

    t2 = Transaction(
        transaction_id="2", user_id="u1", description="Order from Blinkit",
        amount=400.0, currency="INR", direction="debit", status="COMPLETED",
        category="unknown", event_type="expense", event_date=date.today(), flexibility="variable"
    )
    assert categorizer.predict(t2).category == "food"

    t3 = Transaction(
        transaction_id="3", user_id="u1", description="Swiggy food order",
        amount=650.0, currency="INR", direction="debit", status="COMPLETED",
        category="unknown", event_type="expense", event_date=date.today(), flexibility="variable"
    )
    assert categorizer.predict(t3).category == "food"

    t4 = Transaction(
        transaction_id="4", user_id="u1", description="Uber cab ride",
        amount=380.0, currency="INR", direction="debit", status="COMPLETED",
        category="unknown", event_type="expense", event_date=date.today(), flexibility="variable"
    )
    assert categorizer.predict(t4).category == "travel"


def test_financial_state_rolls_up_merchant_categories():
    txs = [
        Transaction(
            transaction_id="tx1",
            user_id="test-user",
            description="UPI-MYNTRA-CLOTHES",
            amount=2500.0,
            currency="INR",
            direction="debit",
            category="unknown",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="tx2",
            user_id="test-user",
            description="SWIGGY-LUNCH-ORDER",
            amount=650.0,
            currency="INR",
            direction="debit",
            category="debit",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="tx3",
            user_id="test-user",
            description="BLINKIT-QUICK-GROCERY",
            amount=420.0,
            currency="INR",
            direction="debit",
            category="unknown",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="tx4",
            user_id="test-user",
            description="UBER-TRIP-DELHI",
            amount=380.0,
            currency="INR",
            direction="debit",
            category="other",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
    ]

    engine = FinancialStateEngine(user_id="test-user")
    state = engine.calculate_state(txs)

    cat_map = {c.category: c.total_amount for c in state.category_spending}
    assert cat_map.get("shopping") == 2500.0
    assert cat_map.get("food") == 1070.0  # Swiggy 650 + Blinkit 420
    assert cat_map.get("travel") == 380.0  # Uber 380


def test_intent_parser_detects_merchant_spending():
    parser = IntentParser()

    p1 = parser.parse("How much did I spend on Myntra?")
    assert p1.intent == IntentType.SPENDING_ANALYSIS
    assert p1.merchant == "Myntra"
    assert p1.category == "shopping"

    p2 = parser.parse("What are my Swiggy and Blinkit food expenses?")
    assert p2.intent == IntentType.SPENDING_ANALYSIS
    assert p2.category == "food"

    p3 = parser.parse("Uber travel cost last month")
    assert p3.intent == IntentType.SPENDING_ANALYSIS
    assert p3.merchant == "Uber"
    assert p3.category == "travel"

    p4 = parser.parse("Show me the category wise distribution")
    assert p4.intent == IntentType.SPENDING_ANALYSIS


def test_spending_analysis_tool_and_response_generator():
    profile = FinancialProfile(
        user_id="test-user",
        home_currency="INR",
        current_available_balance=50000.0,
        minimum_balance_to_keep=15000.0,
        financial_priorities=[],
        expense_categories_to_protect=[],
        expense_categories_user_is_willing_to_reduce=[],
        expense_categories_user_is_willing_to_stop=[],
        payment_methods_user_will_consider=[],
    )
    txs = [
        Transaction(
            transaction_id="t1",
            user_id="test-user",
            description="Payment to Myntra",
            amount=3000.0,
            currency="INR",
            direction="debit",
            category="shopping",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="t2",
            user_id="test-user",
            description="Order from Amazon India",
            amount=4500.0,
            currency="INR",
            direction="debit",
            category="shopping",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="t3",
            user_id="test-user",
            description="Swiggy Delivery",
            amount=1200.0,
            currency="INR",
            direction="debit",
            category="food",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="t4",
            user_id="test-user",
            description="Blinkit Quick Mart",
            amount=800.0,
            currency="INR",
            direction="debit",
            category="food",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
        Transaction(
            transaction_id="t5",
            user_id="test-user",
            description="Uber Ride Airport",
            amount=950.0,
            currency="INR",
            direction="debit",
            category="travel",
            flexibility="variable",
            status="COMPLETED",
            event_type="expense",
            event_date=date.today(),
        ),
    ]

    args = SpendingAnalysisArgs()
    result = execute_spending_analysis(args, profile, txs)

    assert result["total_expenses"] == 10450.0
    assert "category_distribution" in result
    assert result["detected_apps_count"] == 5

    # Check that apps are correctly grouped inside category_distribution
    cat_dist_map = {c["category"]: c for c in result["category_distribution"]}
    assert "shopping" in cat_dist_map
    shopping_apps = {a["name"]: a["amount"] for a in cat_dist_map["shopping"]["apps"]}
    assert shopping_apps.get("Amazon") == 4500.0
    assert shopping_apps.get("Myntra") == 3000.0

    assert "food" in cat_dist_map
    food_apps = {a["name"]: a["amount"] for a in cat_dist_map["food"]["apps"]}
    assert food_apps.get("Swiggy") == 1200.0
    assert food_apps.get("Blinkit") == 800.0

    assert "travel" in cat_dist_map
    travel_apps = {a["name"]: a["amount"] for a in cat_dist_map["travel"]["apps"]}
    assert travel_apps.get("Uber") == 950.0

    # Generate response
    generator = ResponseGenerator()
    intent_obj = IntentParser().parse("show category wise distribution")
    markdown_resp = generator.generate(intent_obj, result, currency="INR")

    # Verify that the response explicitly displays category-wise distribution with detected apps
    assert "Category-Wise Spending Distribution" in markdown_resp
    assert "Shopping" in markdown_resp
    assert "Amazon" in markdown_resp
    assert "Myntra" in markdown_resp
    assert "Food" in markdown_resp
    assert "Swiggy" in markdown_resp
    assert "Blinkit" in markdown_resp
    assert "Travel" in markdown_resp
    assert "Uber" in markdown_resp
