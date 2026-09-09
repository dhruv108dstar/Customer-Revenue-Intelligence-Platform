from __future__ import annotations

import pandas as pd

from src.etl.transform import transform_customers, transform_transactions


def test_transform_customers_handles_missing_values():
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 2, 3],
            "gender": ["Male", None, "Female", "Female"],
            "age": [25, 33, 28, 120],
            "city": ["NYC", None, "Boston", "SF"],
            "state": ["NY", None, "MA", "CA"],
            "region": ["East", None, "East", "West"],
            "signup_date": ["2020-01-01", "2021-01-01", "2021-02-01", "2022-01-01"],
            "tenure_months": [24, 12, 9, 130],
            "plan_id": ["P001", "P002", "P002", "P003"],
            "contract_type": ["Month-to-Month", "12 Month", "12 Month", "24 Month"],
            "payment_method": ["Credit Card", "Debit Card", "Debit Card", "Cash"],
            "device_type": ["Smartphone", "Tablet", "Tablet", "5G Device"],
            "churn": [0, 1, 1, 0],
        }
    )

    result = transform_customers(df)
    assert result["customer_id"].is_unique
    assert result["age"].between(18, 90).all()
    assert result["tenure_months"].between(1, 120).all()
    assert "Unknown" in result["gender"].values


def test_transform_transactions_removes_negative_amounts():
    df = pd.DataFrame(
        {
            "transaction_id": [1, 2, 3],
            "customer_id": [10, 11, None],
            "transaction_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "transaction_type": ["Recharge", "Bill Payment", "Data Pack"],
            "amount": [50.0, -10.0, 25.0],
            "payment_status": ["Paid", "Paid", "Paid"],
        }
    )

    result = transform_transactions(df)
    assert result["amount"].ge(0).all()
    assert result["customer_id"].notna().all()
    assert result["transaction_date"].notna().all()
