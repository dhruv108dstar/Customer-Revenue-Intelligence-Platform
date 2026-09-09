from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import RAW_DATA_DIR


def extract_dataset(file_name: str) -> pd.DataFrame:
    path = Path(RAW_DATA_DIR) / f"{file_name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing raw dataset: {path}")
    return pd.read_csv(path)


def extract_all() -> dict[str, pd.DataFrame]:
    return {
        "customers": extract_dataset("customers"),
        "plans": extract_dataset("plans"),
        "transactions": extract_dataset("transactions"),
        "usage": extract_dataset("usage"),
        "complaints": extract_dataset("complaints"),
        "payments": extract_dataset("payments"),
    }
