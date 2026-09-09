from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_churn_dataset(feature_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_columns = [
        "tenure_months",
        "monthly_revenue",
        "complaint_count",
        "data_used_total",
        "late_payment_days",
    ]
    model_df = feature_df[feature_columns + ["churn"]].copy()
    model_df[feature_columns] = model_df[feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    model_df["churn"] = pd.to_numeric(model_df["churn"], errors="coerce").fillna(0).astype(int)

    X = model_df.drop(columns=["churn"])
    y = model_df["churn"]
    return X, y


def train_baseline_models(feature_df: pd.DataFrame) -> dict[str, object]:
    X, y = build_churn_dataset(feature_df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    models = {
        "logistic_regression": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
            ]
        ),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        prob = model.predict_proba(X_test)[:, 1]
        results[name] = {
            "model": model,
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "f1": f1_score(y_test, preds, zero_division=0),
            "roc_auc": roc_auc_score(y_test, prob),
            "confusion_matrix": confusion_matrix(y_test, preds),
            "test_customer_ids": X_test.index,
            "test_probabilities": prob,
        }
    return results
