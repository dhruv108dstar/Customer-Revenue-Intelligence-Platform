from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SQL_DIR = BASE_DIR / "sql"
REPORTS_DIR = BASE_DIR / "reports"

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "customer_revenue_intelligence")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

DB_URL = (
    f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

PLAN_TABLE = "plans"
CUSTOMER_TABLE = "customers"
TRANSACTION_TABLE = "transactions"
USAGE_TABLE = "usage"
COMPLAINT_TABLE = "complaints"
PAYMENT_TABLE = "payments"

RAW_FILES = {
    "customers": RAW_DATA_DIR / "customers.csv",
    "plans": RAW_DATA_DIR / "plans.csv",
    "transactions": RAW_DATA_DIR / "transactions.csv",
    "usage": RAW_DATA_DIR / "usage.csv",
    "complaints": RAW_DATA_DIR / "complaints.csv",
    "payments": RAW_DATA_DIR / "payments.csv",
}

PROCESSED_FILES = {
    "customers": PROCESSED_DATA_DIR / "customers_clean.csv",
    "plans": PROCESSED_DATA_DIR / "plans_clean.csv",
    "transactions": PROCESSED_DATA_DIR / "transactions_clean.csv",
    "usage": PROCESSED_DATA_DIR / "usage_clean.csv",
    "complaints": PROCESSED_DATA_DIR / "complaints_clean.csv",
    "payments": PROCESSED_DATA_DIR / "payments_clean.csv",
}
