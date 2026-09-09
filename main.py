from __future__ import annotations

from src.etl.extract import extract_all
from src.etl.load import load_all
from src.etl.transform import (
    transform_complaints,
    transform_customers,
    transform_payments,
    transform_plans,
    transform_transactions,
    transform_usage,
)
from sqlalchemy import text

from src.config import SQL_DIR
from src.config import PROCESSED_FILES
from src.etl.validate import calculate_quality_metrics
from src.etl.transform import enforce_referential_integrity
from src.utils.database import get_engine
from src.utils.logger import get_logger

logger = get_logger("main")


def ensure_database() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))


def apply_analytics_views() -> None:
    views_sql = (SQL_DIR / "05_analytics_views.sql").read_text(encoding="utf-8")
    engine = get_engine()
    with engine.begin() as connection:
        for statement in views_sql.split(";"):
            if statement.strip():
                connection.execute(text(statement))


def save_processed_data(processed: dict[str, object]) -> None:
    for table_name, dataframe in processed.items():
        output_path = PROCESSED_FILES[table_name]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(output_path, index=False)
        metrics = calculate_quality_metrics(dataframe)
        logger.info("Validated %s: %s", table_name, metrics)


def run_pipeline() -> None:
    logger.info("Extraction started")
    raw = extract_all()
    logger.info("Extracted %s raw datasets", len(raw))

    logger.info("Cleaning started")
    customers = transform_customers(raw["customers"])
    plans = transform_plans(raw["plans"])
    transactions = transform_transactions(raw["transactions"])
    usage = transform_usage(raw["usage"])
    complaints = transform_complaints(raw["complaints"])
    payments = transform_payments(raw["payments"])

    processed = {
        "customers": customers,
        "plans": plans,
        "transactions": transactions,
        "usage": usage,
        "complaints": complaints,
        "payments": payments,
    }

    logger.info("Validation started")
    save_processed_data(processed)
    integrity = enforce_referential_integrity(
        customers,
        plans,
        transactions,
        usage,
        complaints,
        payments,
    )
    logger.info("Referential integrity: %s", integrity)

    for table_name, df in processed.items():
        logger.info("Prepared %s rows for %s", len(df), table_name)

    logger.info("Database loading")
    load_all(processed)
    logger.info("Applying analytics views")
    apply_analytics_views()
    logger.info("Pipeline completion")


def main() -> None:
    try:
        run_pipeline()
    except Exception as exc:
        logger.exception("Pipeline error: %s", exc)
        raise


if __name__ == "__main__":
    main()
