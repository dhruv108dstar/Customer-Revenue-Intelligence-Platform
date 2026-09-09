from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DB_URL, SQL_DIR
from src.etl.validate import calculate_quality_metrics
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_dataframe_to_sql(df: pd.DataFrame, table_name: str, engine, if_exists: str = "append") -> None:
    logger.info("Loading %s rows into %s", len(df), table_name)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False, chunksize=5_000, method="multi")


def initialize_schema(engine) -> None:
    with engine.begin() as connection:
        for file_name in ("01_schema.sql", "02_tables.sql", "03_indexes.sql"):
            schema_sql = (SQL_DIR / file_name).read_text(encoding="utf-8")
            for statement in schema_sql.split(";"):
                if statement.strip():
                    connection.execute(text(statement))


def build_date_dimension(dataframes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    date_columns = {
        "transaction_date": dataframes["transactions"],
        "usage_date": dataframes["usage"],
        "complaint_date": dataframes["complaints"],
        "payment_date": dataframes["payments"],
    }
    dates = pd.concat(
        [frame[column].dropna().rename("date_id") for column, frame in date_columns.items()],
        ignore_index=True,
    ).drop_duplicates()
    dates = pd.to_datetime(dates).sort_values()
    return pd.DataFrame(
        {
            "date_id": dates.dt.date,
            "year_number": dates.dt.year,
            "month_number": dates.dt.month,
            "month_name": dates.dt.month_name(),
            "quarter": dates.dt.quarter,
            "day_number": dates.dt.day,
            "is_month_end": dates.dt.is_month_end,
        }
    )


def build_region_dimension(customers: pd.DataFrame) -> pd.DataFrame:
    regions = customers[["region"]].drop_duplicates().rename(columns={"region": "region_name"})
    regions["country_name"] = "US"
    regions["service_quality_score"] = None
    return regions


def load_all(dataframes: dict[str, pd.DataFrame]) -> None:
    engine = create_engine(DB_URL)
    initialize_schema(engine)

    load_order = [
        ("dim_plan", dataframes["plans"]),
        ("dim_customer", dataframes["customers"]),
        ("dim_date", build_date_dimension(dataframes)),
        ("dim_region", build_region_dimension(dataframes["customers"])),
        ("fact_transactions", dataframes["transactions"]),
        ("fact_usage", dataframes["usage"]),
        ("fact_complaints", dataframes["complaints"]),
        ("fact_payments", dataframes["payments"]),
    ]

    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE fact_payments, fact_complaints, fact_usage, "
                "fact_transactions, dim_date, dim_region, dim_customer, dim_plan "
                "RESTART IDENTITY CASCADE"
            )
        )
        connection.execute(text("TRUNCATE TABLE quality_summary"))

    for table_name, df in load_order:
        load_dataframe_to_sql(df, table_name, engine)

    quality_rows = []
    for table_name, df in dataframes.items():
        metrics = calculate_quality_metrics(df)
        quality_rows.append(
            {
                "table_name": table_name,
                "records": metrics["records"],
                "duplicate_rate_pct": metrics["duplicate_rate_pct"],
                "missing_rate_pct": metrics["missing_rate_pct"],
                "overall_quality_score": max(
                    0.0,
                    100.0 - metrics["duplicate_rate_pct"] - metrics["missing_rate_pct"],
                ),
            }
        )
    load_dataframe_to_sql(pd.DataFrame(quality_rows), "quality_summary", engine)
