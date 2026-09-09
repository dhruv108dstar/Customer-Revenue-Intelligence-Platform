from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean_numeric_series(series: pd.Series, lower_bound: float | None = None, upper_bound: float | None = None) -> pd.Series:
    cleaned = series.copy()
    cleaned = cleaned.replace({"": np.nan, "NULL": np.nan, None: np.nan})
    cleaned = pd.to_numeric(cleaned, errors="coerce")
    if lower_bound is not None:
        cleaned = cleaned.where(cleaned >= lower_bound)
    if upper_bound is not None:
        cleaned = cleaned.where(cleaned <= upper_bound)
    return cleaned


def deduplicate_frame(df: pd.DataFrame, key_columns: list[str]) -> tuple[pd.DataFrame, int]:
    before = len(df)
    df_clean = df.drop_duplicates(subset=key_columns)
    removed = before - len(df_clean)
    return df_clean, removed


def normalize_dates(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    cleaned = df.copy()
    for column in date_columns:
        cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")
    return cleaned


def validate_customer_ids(df: pd.DataFrame, customer_id_col: str = "customer_id") -> pd.DataFrame:
    cleaned = df.copy()
    cleaned[customer_id_col] = pd.to_numeric(cleaned[customer_id_col], errors="coerce")
    cleaned = cleaned.dropna(subset=[customer_id_col])
    cleaned = cleaned[cleaned[customer_id_col].astype(int) > 0]
    return cleaned


def safe_round(df: pd.DataFrame, columns: list[str], decimals: int = 2) -> pd.DataFrame:
    cleaned = df.copy()
    for column in columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].round(decimals)
    return cleaned


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning customers table")
    cleaned = df.copy()
    cleaned["signup_date"] = pd.to_datetime(cleaned["signup_date"], errors="coerce")
    cleaned["gender"] = cleaned["gender"].fillna("Unknown")
    cleaned["city"] = cleaned["city"].fillna("Unknown")
    cleaned["state"] = cleaned["state"].fillna("Unknown")
    cleaned["region"] = cleaned["region"].fillna("Unknown")
    cleaned["age"] = pd.to_numeric(cleaned["age"], errors="coerce").clip(lower=18, upper=90)
    cleaned["tenure_months"] = pd.to_numeric(cleaned["tenure_months"], errors="coerce").clip(lower=1, upper=120)
    cleaned["churn"] = pd.to_numeric(cleaned["churn"], errors="coerce").fillna(0).clip(lower=0, upper=1)
    cleaned["customer_id"] = pd.to_numeric(cleaned["customer_id"], errors="coerce")
    cleaned = cleaned.dropna(subset=["customer_id", "signup_date"])
    cleaned, dupes = deduplicate_frame(cleaned, ["customer_id"])
    logger.info("Removed %s duplicate customer records", dupes)
    return cleaned


def transform_plans(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["monthly_fee"] = clean_numeric_series(cleaned["monthly_fee"], lower_bound=0)
    cleaned["data_limit_gb"] = clean_numeric_series(cleaned["data_limit_gb"], lower_bound=0)
    cleaned["voice_limit_minutes"] = clean_numeric_series(cleaned["voice_limit_minutes"], lower_bound=0)
    cleaned["sms_limit"] = clean_numeric_series(cleaned["sms_limit"], lower_bound=0)
    cleaned["plan_id"] = cleaned["plan_id"].astype(str)
    return cleaned


def transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_dates(df, ["transaction_date"])
    cleaned["amount"] = clean_numeric_series(cleaned["amount"], lower_bound=0)
    cleaned["transaction_type"] = cleaned["transaction_type"].fillna("Unknown")
    cleaned["payment_status"] = cleaned["payment_status"].fillna("Unknown")
    cleaned["customer_id"] = pd.to_numeric(cleaned["customer_id"], errors="coerce")
    cleaned = cleaned.dropna(subset=["customer_id", "transaction_date"]).copy()
    cleaned = cleaned[cleaned["amount"] >= 0]
    cleaned["amount"] = cleaned["amount"].round(2)
    return cleaned


def transform_usage(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_dates(df, ["usage_date"])
    cleaned["data_used_gb"] = clean_numeric_series(cleaned["data_used_gb"], lower_bound=0)
    cleaned["voice_minutes"] = clean_numeric_series(cleaned["voice_minutes"], lower_bound=0)
    cleaned["sms_count"] = clean_numeric_series(cleaned["sms_count"], lower_bound=0)
    cleaned["roaming_minutes"] = clean_numeric_series(cleaned["roaming_minutes"], lower_bound=0)
    cleaned["customer_id"] = pd.to_numeric(cleaned["customer_id"], errors="coerce")
    cleaned = cleaned.dropna(subset=["customer_id", "usage_date"]).copy()
    return cleaned


def transform_complaints(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_dates(df, ["complaint_date"])
    cleaned["category"] = cleaned["category"].fillna("Unknown")
    cleaned["status"] = cleaned["status"].fillna("Unknown")
    cleaned["severity"] = cleaned["severity"].fillna("Medium")
    cleaned["resolution_time_hours"] = pd.to_numeric(cleaned["resolution_time_hours"], errors="coerce")
    cleaned["customer_id"] = pd.to_numeric(cleaned["customer_id"], errors="coerce")
    cleaned = cleaned.dropna(subset=["customer_id", "complaint_date"]).copy()
    return cleaned


def transform_payments(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = normalize_dates(df, ["payment_date"])
    cleaned["amount"] = clean_numeric_series(cleaned["amount"], lower_bound=0)
    cleaned["days_late"] = pd.to_numeric(cleaned["days_late"], errors="coerce").fillna(0).clip(lower=0)
    cleaned["payment_status"] = cleaned["payment_status"].fillna("Unknown")
    cleaned["payment_method"] = cleaned["payment_method"].fillna("Unknown")
    cleaned["customer_id"] = pd.to_numeric(cleaned["customer_id"], errors="coerce")
    cleaned = cleaned.dropna(subset=["customer_id", "payment_date"]).copy()
    return cleaned


def enforce_referential_integrity(customers: pd.DataFrame, plans: pd.DataFrame, transactions: pd.DataFrame, usage: pd.DataFrame, complaints: pd.DataFrame, payments: pd.DataFrame) -> dict[str, Any]:
    valid_customer_ids = set(customers["customer_id"].astype(int).tolist())
    valid_plan_ids = set(plans["plan_id"].astype(str).tolist())

    orphan_counts = {
        "transactions": int((~transactions["customer_id"].isin(valid_customer_ids)).sum()),
        "usage": int((~usage["customer_id"].isin(valid_customer_ids)).sum()),
        "complaints": int((~complaints["customer_id"].isin(valid_customer_ids)).sum()),
        "payments": int((~payments["customer_id"].isin(valid_customer_ids)).sum()),
    }

    invalid_plan_map = set(customers["plan_id"].astype(str).tolist()) - valid_plan_ids
    return {
        "valid_customer_ids": len(valid_customer_ids),
        "valid_plan_ids": len(valid_plan_ids),
        "orphan_counts": orphan_counts,
        "invalid_plan_refs": len(invalid_plan_map),
    }
