from __future__ import annotations

from typing import Any

import pandas as pd


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> tuple[bool, list[str]]:
    missing = [column for column in required_columns if column not in df.columns]
    return len(missing) == 0, missing


def calculate_quality_metrics(df: pd.DataFrame) -> dict[str, Any]:
    total = len(df)
    missing_rate = float(df.isna().mean().mean() * 100 if total else 0)
    duplicate_rate = float(df.duplicated().mean() * 100 if total else 0)
    return {
        "records": total,
        "duplicate_rate_pct": duplicate_rate,
        "missing_rate_pct": missing_rate,
    }


def check_future_dates(df: pd.DataFrame, date_columns: list[str]) -> dict[str, int]:
    results = {}
    for column in date_columns:
        if column in df.columns:
            future_rows = int((pd.to_datetime(df[column], errors="coerce") > pd.Timestamp.now()).sum())
            results[column] = future_rows
    return results


def revenue_reconciliation(transactions: pd.DataFrame, payments: pd.DataFrame) -> dict[str, float]:
    tx_total = float(transactions["amount"].sum()) if not transactions.empty else 0.0
    payment_total = float(payments["amount"].sum()) if not payments.empty else 0.0
    difference = abs(tx_total - payment_total)
    return {"transaction_total": tx_total, "payment_total": payment_total, "difference": difference}
