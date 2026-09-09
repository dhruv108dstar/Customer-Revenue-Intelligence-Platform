from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import RAW_DATA_DIR


RNG_SEED = 42


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1 / (1 + np.exp(-x))


def generate_plans() -> pd.DataFrame:
    plans = pd.DataFrame(
        [
            ("P001", "Starter 15", "Basic", 20.0, 15, 300, 200, "Month-to-Month"),
            ("P002", "Starter 25", "Basic", 25.0, 25, 500, 300, "Month-to-Month"),
            ("P003", "Flex 40", "Standard", 40.0, 40, 800, 500, "12 Month"),
            ("P004", "Flex 60", "Standard", 60.0, 60, 1200, 800, "12 Month"),
            ("P005", "Flex 80", "Standard", 80.0, 80, 1800, 1000, "24 Month"),
            ("P006", "Plus 100", "Premium", 100.0, 100, 2400, 1200, "Month-to-Month"),
            ("P007", "Plus 150", "Premium", 150.0, 150, 3000, 1500, "12 Month"),
            ("P008", "Plus 200", "Premium", 200.0, 200, 4000, 2000, "24 Month"),
            ("P009", "Business Lite", "Business", 120.0, 120, 2500, 1500, "12 Month"),
            ("P010", "Business Pro", "Business", 180.0, 180, 5000, 2500, "24 Month"),
            ("P011", "Enterprise 250", "Enterprise", 250.0, 250, 7000, 4000, "24 Month"),
            ("P012", "Enterprise 350", "Enterprise", 350.0, 350, 9000, 5000, "24 Month"),
            ("P013", "Family 100", "Family", 110.0, 100, 2200, 1500, "Month-to-Month"),
            ("P014", "Family 180", "Family", 180.0, 180, 3500, 2000, "12 Month"),
            ("P015", "Unlimited Max", "Premium", 260.0, 400, 10000, 10000, "24 Month"),
        ],
        columns=[
            "plan_id",
            "plan_name",
            "plan_type",
            "monthly_fee",
            "data_limit_gb",
            "voice_limit_minutes",
            "sms_limit",
            "contract_type",
        ],
    )
    return plans


def generate_customers(n_customers: int = 50000, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    regions = [
        ("North", ["Seattle", "Denver", "Minneapolis", "Chicago", "Boston"]),
        ("South", ["Dallas", "Atlanta", "Miami", "Houston", "Charlotte"]),
        ("East", ["New York", "Philadelphia", "Boston", "Baltimore", "Washington"]),
        ("West", ["Los Angeles", "San Francisco", "San Diego", "Phoenix", "Portland"]),
        ("Central", ["Detroit", "Kansas City", "St. Louis", "Cincinnati", "Nashville"]),
    ]
    states = {
        "Seattle": "WA", "Denver": "CO", "Minneapolis": "MN", "Chicago": "IL", "Boston": "MA",
        "Dallas": "TX", "Atlanta": "GA", "Miami": "FL", "Houston": "TX", "Charlotte": "NC",
        "New York": "NY", "Philadelphia": "PA", "Baltimore": "MD", "Washington": "DC",
        "Los Angeles": "CA", "San Francisco": "CA", "San Diego": "CA", "Phoenix": "AZ", "Portland": "OR",
        "Detroit": "MI", "Kansas City": "MO", "St. Louis": "MO", "Cincinnati": "OH", "Nashville": "TN",
    }
    city_by_region = {city: region for region, cities in regions for city in cities}
    region_quality = {"North": 0.1, "South": -0.15, "East": 0.03, "West": 0.18, "Central": -0.12}
    city_choices = [city for _, cities in regions for city in cities]

    customers = pd.DataFrame(
        {
            "customer_id": np.arange(1, n_customers + 1),
            "gender": rng.choice(["Male", "Female", "Non-binary"], size=n_customers, p=[0.49, 0.49, 0.02]),
            "age": np.clip(rng.normal(38, 13, n_customers), 18, 82).round().astype(int),
            "city": rng.choice(city_choices, size=n_customers),
        }
    )
    customers["state"] = customers["city"].map(states)
    customers["region"] = customers["city"].map(city_by_region)

    signup_months_ago = rng.integers(1, 72, size=n_customers)
    signup_offsets = signup_months_ago * 30 + rng.integers(0, 30, size=n_customers)
    customers["signup_date"] = pd.Timestamp("2020-01-01") - pd.to_timedelta(signup_offsets, unit="D")
    customers["signup_date"] = pd.to_datetime(customers["signup_date"]).dt.normalize()
    customers["tenure_months"] = np.clip((pd.Timestamp("2025-01-01") - customers["signup_date"]).dt.days // 30, 1, 120).astype(int)

    plans = generate_plans()
    plan_prob = np.array([0.18, 0.12, 0.14, 0.12, 0.08, 0.10, 0.08, 0.05, 0.04, 0.03, 0.02, 0.01, 0.06, 0.04, 0.03], dtype=float)
    plan_prob = plan_prob / plan_prob.sum()
    customers["plan_id"] = rng.choice(plans["plan_id"].to_numpy(), size=n_customers, p=plan_prob)
    customers["contract_type"] = customers["plan_id"].map(plans.set_index("plan_id")["contract_type"])
    customers["payment_method"] = rng.choice(["Credit Card", "Debit Card", "Bank Transfer", "Cash", "Wallet"], size=n_customers, p=[0.38, 0.24, 0.18, 0.08, 0.12])
    customers["device_type"] = rng.choice(["Smartphone", "Tablet", "Feature Phone", "5G Device"], size=n_customers, p=[0.62, 0.12, 0.08, 0.18])

    plan_tier_map = {
        "P001": 0.2, "P002": 0.2, "P003": 0.6, "P004": 0.6, "P005": 0.6,
        "P006": 1.0, "P007": 1.0, "P008": 1.0, "P009": 1.3, "P010": 1.3,
        "P011": 1.6, "P012": 1.6, "P013": 0.8, "P014": 0.8, "P015": 1.0,
    }
    tenure_factor = -0.05 * customers["tenure_months"]
    payment_delay_factor = rng.normal(0, 1, n_customers)
    region_factor = customers["region"].map(region_quality).to_numpy()
    age_factor = (customers["age"] - 40) * 0.01
    plan_tier = customers["plan_id"].map(plan_tier_map).to_numpy()
    churn_logit = -0.8 + tenure_factor + 0.8 * payment_delay_factor + 0.4 * region_factor + 0.2 * age_factor - 0.15 * plan_tier
    churn_prob = sigmoid(churn_logit)
    customers["churn"] = (rng.random(n_customers) < churn_prob).astype(int)
    return customers


def _allocate_counts(total_rows: int, n_customers: int, base_lambda: float) -> np.ndarray:
    counts = np.random.default_rng(RNG_SEED + 99).poisson(base_lambda, n_customers)
    diff = total_rows - counts.sum()
    if diff != 0:
        counts[: abs(diff)] += 1 if diff > 0 else -1
    return counts


def generate_transactions(customers: pd.DataFrame, plans: pd.DataFrame, n_transactions: int = 1_000_000, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1)
    plan_lookup = plans.set_index("plan_id")
    customer_ids = customers["customer_id"].to_numpy()
    plan_ids = customers["plan_id"].to_numpy()
    counts = _allocate_counts(n_transactions, len(customers), 20)

    repeated_customer_ids = np.repeat(customer_ids, counts)
    repeated_plan_ids = np.repeat(plan_ids, counts)
    total_rows = len(repeated_customer_ids)
    months = rng.integers(0, 36, total_rows)
    days = rng.integers(0, 28, total_rows)
    dates = pd.Timestamp("2021-01-01") + pd.to_timedelta(months * 30 + days, unit="D")

    tx_types = np.array(["Recharge", "Bill Payment", "Addon Purchase", "Data Pack", "Roaming", "International Calling"])
    tx_probs = np.array([0.28, 0.24, 0.18, 0.15, 0.09, 0.06])
    tx_choice = rng.choice(tx_types, size=total_rows, p=tx_probs)

    base_amounts = np.array([float(plan_lookup.loc[plan_id, "monthly_fee"]) / 3 for plan_id in repeated_plan_ids])
    amounts = np.empty(total_rows, dtype=float)
    for idx, t in enumerate(tx_choice):
        if t == "Recharge":
            amounts[idx] = max(0.0, float(rng.normal(base_amounts[idx] * 2.5, base_amounts[idx] * 0.8)))
        elif t == "Bill Payment":
            amounts[idx] = max(0.0, float(rng.normal(base_amounts[idx] * 1.6, base_amounts[idx] * 0.7)))
        elif t == "Addon Purchase":
            amounts[idx] = max(0.0, float(rng.normal(base_amounts[idx] * 1.2, base_amounts[idx] * 0.5)))
        elif t == "Data Pack":
            amounts[idx] = max(0.0, float(rng.normal(base_amounts[idx] * 0.8, base_amounts[idx] * 0.4)))
        elif t == "Roaming":
            amounts[idx] = max(0.0, float(rng.normal(base_amounts[idx] * 1.8, base_amounts[idx] * 0.9)))
        else:
            amounts[idx] = max(0.0, float(rng.normal(base_amounts[idx] * 2.3, base_amounts[idx] * 1.1)))

    statuses = np.array(["Paid", "Pending", "Late"])
    status_probs = np.array([0.8, 0.12, 0.08])
    payment_status = rng.choice(statuses, size=total_rows, p=status_probs)

    df = pd.DataFrame(
        {
            "transaction_id": np.arange(1, total_rows + 1),
            "customer_id": repeated_customer_ids.astype(int),
            "transaction_date": dates,
            "transaction_type": tx_choice,
            "amount": np.round(amounts, 2),
            "payment_status": payment_status,
        }
    )
    return df


def generate_usage(customers: pd.DataFrame, n_usage: int = 1_000_000, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 2)
    usage_lookup = generate_plans().set_index("plan_id")
    counts = _allocate_counts(n_usage, len(customers), 20)
    customer_ids = np.repeat(customers["customer_id"].to_numpy(), counts)
    plan_ids = np.repeat(customers["plan_id"].to_numpy(), counts)
    total_rows = len(customer_ids)
    dates = pd.Timestamp("2021-01-01") + pd.to_timedelta(rng.integers(0, 36 * 30, total_rows), unit="D")

    data_limits = np.array([float(usage_lookup.loc[p, "data_limit_gb"]) for p in plan_ids])
    voice_limits = np.array([float(usage_lookup.loc[p, "voice_limit_minutes"]) for p in plan_ids])
    sms_limits = np.array([float(usage_lookup.loc[p, "sms_limit"]) for p in plan_ids])

    data_used = np.maximum(0.0, rng.gamma(2.2, data_limits / 6.0, size=total_rows))
    voice_minutes = np.maximum(0.0, rng.gamma(2.5, voice_limits / 8.0, size=total_rows))
    sms_count = np.maximum(0.0, rng.gamma(2.0, sms_limits / 10.0, size=total_rows))
    roaming_minutes = np.maximum(0.0, rng.gamma(1.8, 40.0, size=total_rows))

    df = pd.DataFrame(
        {
            "usage_id": np.arange(1, total_rows + 1),
            "customer_id": customer_ids.astype(int),
            "usage_date": dates,
            "data_used_gb": np.round(data_used, 2),
            "voice_minutes": np.round(voice_minutes, 2),
            "sms_count": np.round(sms_count, 2),
            "roaming_minutes": np.round(roaming_minutes, 2),
        }
    )
    return df


def generate_complaints(customers: pd.DataFrame, n_complaints: int = 100_000, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 3)
    categories = np.array(["Network", "Billing", "Internet", "Customer Service", "Roaming", "SIM"])
    statuses = np.array(["Open", "Resolved", "Escalated"])
    customer_ids = rng.integers(1, len(customers) + 1, size=n_complaints)
    dates = pd.Timestamp("2021-01-01") + pd.to_timedelta(rng.integers(0, 36 * 30, size=n_complaints), unit="D")
    categories_out = rng.choice(categories, size=n_complaints)
    resolution_time_hours = np.maximum(1, rng.gamma(3.2, 12, size=n_complaints).astype(int))
    status_out = rng.choice(statuses, size=n_complaints, p=[0.25, 0.6, 0.15])
    severity_out = rng.choice(np.array(["Low", "Medium", "High", "Critical"]), size=n_complaints, p=[0.45, 0.35, 0.15, 0.05])
    return pd.DataFrame(
        {
            "complaint_id": np.arange(1, n_complaints + 1),
            "customer_id": customer_ids,
            "complaint_date": dates,
            "category": categories_out,
            "resolution_time_hours": resolution_time_hours,
            "status": status_out,
            "severity": severity_out,
        }
    )


def generate_payments(customers: pd.DataFrame, n_payments: int = 500_000, seed: int = RNG_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 4)
    customer_ids = rng.integers(1, len(customers) + 1, size=n_payments)
    dates = pd.Timestamp("2021-01-01") + pd.to_timedelta(rng.integers(0, 36 * 30, size=n_payments), unit="D")
    amount = np.round(rng.uniform(10, 250, size=n_payments), 2)
    payment_method = rng.choice(np.array(["Credit Card", "Debit Card", "Bank Transfer", "Wallet"]), size=n_payments)
    payment_status = rng.choice(np.array(["Paid", "Late", "Failed"]), size=n_payments, p=[0.82, 0.13, 0.05])
    days_late = np.where(payment_status == "Late", rng.integers(1, 45, size=n_payments), 0)
    return pd.DataFrame(
        {
            "payment_id": np.arange(1, n_payments + 1),
            "customer_id": customer_ids,
            "payment_date": dates,
            "amount": amount,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "days_late": days_late,
        }
    )


def save_raw_dataframes(data_frames: dict[str, pd.DataFrame], output_dir: Path | str = RAW_DATA_DIR) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in data_frames.items():
        df.to_csv(output_dir / f"{name}.csv", index=False)


def main() -> None:
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    plans = generate_plans()
    customers = generate_customers(n_customers=50000)
    transactions = generate_transactions(customers, plans, n_transactions=1_000_000)
    usage = generate_usage(customers, n_usage=1_000_000)
    complaints = generate_complaints(customers, n_complaints=100_000)
    payments = generate_payments(customers, n_payments=500_000)

    save_raw_dataframes(
        {
            "plans": plans,
            "customers": customers,
            "transactions": transactions,
            "usage": usage,
            "complaints": complaints,
            "payments": payments,
        },
        output_dir=RAW_DATA_DIR,
    )

    print(f"Generated customers: {len(customers):,}")
    print(f"Generated transactions: {len(transactions):,}")
    print(f"Generated usage: {len(usage):,}")
    print(f"Generated complaints: {len(complaints):,}")
    print(f"Generated payments: {len(payments):,}")


if __name__ == "__main__":
    main()
