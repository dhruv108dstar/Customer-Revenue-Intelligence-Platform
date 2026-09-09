from __future__ import annotations

import pandas as pd


def summarize_customer_kpis(customer_df: pd.DataFrame) -> pd.DataFrame:
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


def summarize_plan_performance(plan_df: pd.DataFrame, revenue_df: pd.DataFrame) -> pd.DataFrame:
    merged = plan_df.merge(revenue_df, on="plan_id", how="left")
    merged["revenue_share_pct"] = merged["total_revenue"] / merged["total_revenue"].sum().replace(0, 1)
    return merged
