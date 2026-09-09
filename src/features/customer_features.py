from __future__ import annotations

import pandas as pd


def add_customer_features(customers: pd.DataFrame, transactions: pd.DataFrame, payments: pd.DataFrame, usage: pd.DataFrame, complaints: pd.DataFrame) -> pd.DataFrame:
    customer_df = customers.copy()

    tx_by_customer = transactions.groupby("customer_id")["amount"].sum().rename("monthly_revenue")
    customer_df = customer_df.merge(tx_by_customer, on="customer_id", how="left")

    payment_late = payments.groupby("customer_id")["days_late"].max().rename("max_payment_delay_days")
    customer_df = customer_df.merge(payment_late, on="customer_id", how="left")

    complaint_count = complaints.groupby("customer_id").size().rename("complaint_count")
    customer_df = customer_df.merge(complaint_count, on="customer_id", how="left")

    usage_monthly = usage.groupby("customer_id")["data_used_gb"].sum().rename("total_data_used_gb")
    customer_df = customer_df.merge(usage_monthly, on="customer_id", how="left")

    customer_df["monthly_revenue"] = customer_df["monthly_revenue"].fillna(0)
    customer_df["max_payment_delay_days"] = customer_df["max_payment_delay_days"].fillna(0)
    customer_df["complaint_count"] = customer_df["complaint_count"].fillna(0)
    customer_df["total_data_used_gb"] = customer_df["total_data_used_gb"].fillna(0)
    return customer_df
