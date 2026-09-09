from __future__ import annotations

import pandas as pd

from src.features.revenue_features import calculate_arpu, compute_customer_kpis
from src.models.clv_model import calculate_clv, calculate_revenue_at_risk
from src.models.churn_model import train_baseline_models
from src.models.segmentation import assign_segments


def test_calculate_arpu_uses_active_customer_count():
    revenue_df = pd.DataFrame({"monthly_revenue": [120.0, 80.0, 200.0]})
    assert calculate_arpu(revenue_df, active_customers=3) == 133.33333333333334


def test_compute_customer_kpis_produces_expected_summary():
    customer_df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "tenure_months": [18, 12, 30],
            "monthly_revenue": [90.0, 120.0, 150.0],
            "churn": [0.2, 0.5, 0.1],
            "churn_probability": [0.25, 0.45, 0.12],
            "plan_id": ["P001", "P002", "P003"],
        }
    )

    result = compute_customer_kpis(customer_df)

    assert list(result.columns) == [
        "customer_id",
        "tenure_months",
        "monthly_revenue",
        "churn",
        "churn_probability",
        "plan_id",
        "clv",
        "revenue_at_risk",
    ]
    assert result["clv"].notna().all()
    assert result["revenue_at_risk"].notna().all()


def test_clv_helpers_handle_missing_optional_features():
    customer_df = pd.DataFrame({"customer_id": [1, 2], "monthly_revenue": [100, None]})

    clv = calculate_clv(customer_df, arpu=80)
    risk = calculate_revenue_at_risk(customer_df)

    assert clv["clv"].notna().all()
    assert risk["revenue_at_risk"].tolist() == [10.0, 0.0]


def test_models_train_and_assign_business_segments():
    rows = 20
    feature_df = pd.DataFrame(
        {
            "tenure_months": range(1, rows + 1),
            "monthly_revenue": [50 + index * 10 for index in range(rows)],
            "complaint_count": [index % 4 for index in range(rows)],
            "data_used_total": [100 + index * 5 for index in range(rows)],
            "late_payment_days": [index % 7 for index in range(rows)],
            "churn": [index % 2 for index in range(rows)],
            "transaction_frequency": [index + 1 for index in range(rows)],
            "churn_probability": [0.05 + index / 30 for index in range(rows)],
        }
    )

    results = train_baseline_models(feature_df)
    segments = assign_segments(
        feature_df,
        ["monthly_revenue", "transaction_frequency", "data_used_total", "complaint_count", "churn_probability"],
        k=4,
    )

    assert set(results) == {"logistic_regression", "random_forest"}
    assert all(0 <= result["roc_auc"] <= 1 for result in results.values())
    assert segments["segment_name"].notna().all()
