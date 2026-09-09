from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config import PROCESSED_FILES, REPORTS_DIR
from src.features.churn_features import create_churn_features
from src.models.churn_model import train_baseline_models
from src.models.clv_model import calculate_revenue_at_risk
from src.models.segmentation import assign_segments


MODEL_OUTPUT_DIR = REPORTS_DIR / "model_outputs"


def load_processed_data() -> dict[str, pd.DataFrame]:
    return {
        name: pd.read_csv(path)
        for name, path in PROCESSED_FILES.items()
    }


def run() -> None:
    data = load_processed_data()
    features = create_churn_features(
        data["customers"],
        data["transactions"],
        data["payments"],
        data["usage"],
        data["complaints"],
    )

    model_results = train_baseline_models(features)
    best_name = max(model_results, key=lambda name: model_results[name]["roc_auc"])
    best_result = model_results[best_name]
    features["churn_probability"] = best_result["model"].predict_proba(
        features[[
            "tenure_months",
            "monthly_revenue",
            "complaint_count",
            "data_used_total",
            "late_payment_days",
        ]]
    )[:, 1]
    features = calculate_revenue_at_risk(features)

    segment_features = [
        "monthly_revenue",
        "transaction_frequency",
        "data_used_total",
        "complaint_count",
        "churn_probability",
    ]
    features = assign_segments(features, segment_features, k=4)

    MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    features.to_csv(MODEL_OUTPUT_DIR / "customer_scores.csv", index=False)
    comparison = pd.DataFrame(
        [
            {
                "model": name,
                "accuracy": values["accuracy"],
                "precision": values["precision"],
                "recall": values["recall"],
                "f1": values["f1"],
                "roc_auc": values["roc_auc"],
            }
            for name, values in model_results.items()
        ]
    )
    comparison.to_csv(MODEL_OUTPUT_DIR / "model_comparison.csv", index=False)
    (MODEL_OUTPUT_DIR / "run_summary.json").write_text(
        json.dumps(
            {
                "best_model": best_name,
                "customer_count": len(features),
                "revenue_at_risk": float(features["revenue_at_risk"].sum()),
                "segment_counts": features["segment_name"].value_counts().to_dict(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Best churn model: {best_name}")
    print(f"Customers scored: {len(features):,}")
    print(f"Revenue at risk: {features['revenue_at_risk'].sum():,.2f}")


if __name__ == "__main__":
    run()
