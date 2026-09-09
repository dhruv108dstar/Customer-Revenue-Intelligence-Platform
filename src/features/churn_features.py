from __future__ import annotations

import pandas as pd


def create_churn_features(customers: pd.DataFrame, transactions: pd.DataFrame, payments: pd.DataFrame, usage: pd.DataFrame, complaints: pd.DataFrame) -> pd.DataFrame:
    feature_df = customers.copy()

    tx_freq = transactions.groupby("customer_id").size().rename("transaction_frequency")
    feature_df = feature_df.merge(tx_freq, on="customer_id", how="left")

    monthly_revenue = transactions.groupby("customer_id")["amount"].sum().rename("monthly_revenue")
    feature_df = feature_df.merge(monthly_revenue, on="customer_id", how="left")

    late_payments = payments.groupby("customer_id")["days_late"].sum().rename("late_payment_days")
    feature_df = feature_df.merge(late_payments, on="customer_id", how="left")

    complaint_count = complaints.groupby("customer_id").size().rename("complaint_count")
    feature_df = feature_df.merge(complaint_count, on="customer_id", how="left")

    usage_summary = usage.groupby("customer_id")["data_used_gb"].sum().rename("data_used_total")
    feature_df = feature_df.merge(usage_summary, on="customer_id", how="left")

    feature_df["transaction_frequency"] = feature_df["transaction_frequency"].fillna(0)
    feature_df["monthly_revenue"] = feature_df["monthly_revenue"].fillna(0)
    feature_df["late_payment_days"] = feature_df["late_payment_days"].fillna(0)
    feature_df["complaint_count"] = feature_df["complaint_count"].fillna(0)
    feature_df["data_used_total"] = feature_df["data_used_total"].fillna(0)
    return feature_df
