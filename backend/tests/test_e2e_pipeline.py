import pytest
from datetime import datetime, timedelta

def test_full_e2e_pipeline_csv(client, test_user_token):
    # 1. Prepare multi-month synthetic CSV statement
    lines = ["date,description,amount,type"]
    now = datetime.now()
    for m in range(4):
        for i in range(1, 28, 5):
            d = now - timedelta(days=(m * 30 + i))
            d_str = d.strftime("%Y-%m-%d")
            lines.append(f"{d_str},Tech Corp Salary,5000.00,credit")
            lines.append(f"{d_str},Whole Foods Market,120.00,debit")
            lines.append(f"{d_str},Uber Trip,35.00,debit")
            lines.append(f"{d_str},Apartment Rent,1500.00,debit")
    csv_bytes = "\n".join(lines).encode("utf-8")

    # 2. Upload statement
    headers = {"Authorization": f"Bearer {test_user_token}"}
    files = {"file": ("statement.csv", csv_bytes, "text/csv")}
    upload_res = client.post("/api/statements/upload", files=files, headers=headers)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["total_parsed"] > 0
    assert upload_data["data_quality_metrics"]["valid_records"] > 0

    # 3. Verify Transaction Retrieval & ML Categorization
    tx_res = client.get("/api/users/transactions?limit=50", headers=headers)
    assert tx_res.status_code == 200
    transactions = tx_res.json()
    assert len(transactions) > 0

    # Verify categories were assigned by ML model
    categories = {t["category"].lower() for t in transactions}
    assert "salary" in categories or "income" in categories
    assert any(c in ["groceries", "food", "transport", "housing", "rent"] for c in categories)

    # 4. Verify Financial State Calculations
    state_res = client.get("/api/users/state", headers=headers)
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["income"] > 0
    assert state["expenses"] > 0
    assert state["cash_flow"] == state["income"] - state["expenses"]
    assert len(state["category_spending"]) > 0

    # 5. Verify Forecast Engine
    pred_res = client.get("/api/users/prediction", headers=headers)
    assert pred_res.status_code == 200
    pred = pred_res.json()
    assert pred["available"] is True
    assert len(pred["forecasts"]) > 0

    # 6. Verify What-If Simulator
    whatif_res = client.post(
        "/api/users/what-if",
        headers=headers,
        json={"scenario_type": "reduce_expense", "amount": 200.0}
    )
    assert whatif_res.status_code == 200
    whatif_data = whatif_res.json()
    assert "baseline" in whatif_data
    assert "scenario" in whatif_data
    assert "impact" in whatif_data

    # 7. Verify Copilot Query with Verified Financial Data
    copilot_res = client.post(
        "/api/copilot/query",
        headers=headers,
        json={"message": "What is my total spending?"}
    )
    assert copilot_res.status_code == 200
    copilot_data = copilot_res.json()
    assert copilot_data["status"] == "SUCCESS"
    assert copilot_data["intent"] in ["SPENDING_ANALYSIS", "FINANCIAL_SUMMARY"]
    assert "response" in copilot_data and len(copilot_data["response"]) > 0
