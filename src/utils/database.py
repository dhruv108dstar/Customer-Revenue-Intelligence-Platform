from __future__ import annotations

from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DB_URL


def get_engine():
    return create_engine(DB_URL)


def execute_sql(sql: str, params: dict[str, Any] | None = None) -> None:
    with get_engine().begin() as conn:
        conn.execute(text(sql), params or {})


def read_sql(query: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql_query(query, conn)


def table_exists(engine, table_name: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name);"
            ),
            {"table_name": table_name},
        )
        return result.scalar() is True
