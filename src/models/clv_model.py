from __future__ import annotations

import pandas as pd


def calculate_clv(customer_df: pd.DataFrame, arpu: float, gross_margin: float = 0.65) -> pd.DataFrame:
    result = customer_df.copy()
    monthly_revenue = pd.to_numeric(
        result.get("monthly_revenue", pd.Series(arpu, index=result.index)),
        errors="coerce",
    ).fillna(arpu)
    tenure_months = pd.to_numeric(
        result.get("tenure_months", pd.Series(1, index=result.index)),
        errors="coerce",
    ).fillna(1).clip(lower=1)
    churn_probability = pd.to_numeric(
        result.get("churn_probability", pd.Series(0.1, index=result.index)),
        errors="coerce",
    ).fillna(0.1).clip(lower=0, upper=1)
    result["clv"] = (
        (monthly_revenue * 12 * tenure_months)
        * (1 - churn_probability)
        * gross_margin
    )
    return result


def calculate_revenue_at_risk(customer_df: pd.DataFrame) -> pd.DataFrame:
    result = customer_df.copy()
    result["churn_probability"] = pd.to_numeric(
        result.get("churn_probability", pd.Series(0.1, index=result.index)),
        errors="coerce",
    ).fillna(0.1).clip(lower=0, upper=1)
    monthly_revenue = pd.to_numeric(
        result.get("monthly_revenue", pd.Series(0, index=result.index)),
        errors="coerce",
    ).fillna(0).clip(lower=0)
    result["revenue_at_risk"] = monthly_revenue * result["churn_probability"]
    return result
