from __future__ import annotations

import pandas as pd


def calculate_arpu(revenue_df: pd.DataFrame, active_customers: int) -> float:
    if active_customers == 0:
        return 0.0
    return float(revenue_df["monthly_revenue"].sum() / active_customers)


def compute_customer_kpis(customer_df: pd.DataFrame) -> pd.DataFrame:
    result = customer_df.copy()
    result["clv"] = (
        result.get("monthly_revenue", 0).fillna(0)
        * 12
        * result.get("tenure_months", 1).fillna(1)
        * (1 - result.get("churn", 0.1).fillna(0.1))
        * 0.65
    )
    result["revenue_at_risk"] = (
        result.get("monthly_revenue", 0).fillna(0)
        * result.get("churn_probability", 0.1).fillna(0.1)
    )
    return result


def calculate_clv(row: pd.Series) -> float:
    arpu = row.get("monthly_revenue", 0)
    tenure = row.get("tenure_months", 1)
    frequency = row.get("transaction_frequency", 1)
    churn_probability = row.get("churn_probability", 0.1)
    gross_margin = 0.65
    return float((arpu * 12 * tenure * frequency) * (1 - churn_probability) * gross_margin)
