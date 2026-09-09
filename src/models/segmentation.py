from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def find_optimal_k(data: pd.DataFrame, feature_cols: list[str], max_k: int = 6) -> tuple[int, list[float]]:
    inertia = []
    sil_scores = []
    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(data[feature_cols])
        inertia.append(model.inertia_)
        sil_scores.append(silhouette_score(data[feature_cols], labels))
    best_k = max(range(2, max_k + 1), key=lambda k: sil_scores[k - 2])
    return best_k, sil_scores


def assign_segments(data: pd.DataFrame, feature_cols: list[str], k: int = 4) -> pd.DataFrame:
    if k < 2 or k > len(data):
        raise ValueError("k must be between 2 and the number of rows")
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    data = data.copy()
    values = data[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    scaled_values = StandardScaler().fit_transform(values)
    data["segment_cluster"] = model.fit_predict(scaled_values)
    cluster_summary = data.groupby("segment_cluster")[feature_cols].mean()
    revenue_rank = cluster_summary["monthly_revenue"].rank(method="first", ascending=False)
    churn_rank = cluster_summary["churn_probability"].rank(method="first", ascending=False)
    segment_names = {}
    for cluster_id in cluster_summary.index:
        if revenue_rank[cluster_id] == 1:
            segment_names[cluster_id] = "Premium Loyalists"
        elif churn_rank[cluster_id] == 1:
            segment_names[cluster_id] = "High-Value At Risk"
        elif revenue_rank[cluster_id] == len(cluster_summary):
            segment_names[cluster_id] = "Budget Customers"
        else:
            segment_names[cluster_id] = "Growth Customers"
    data["segment_name"] = data["segment_cluster"].map(segment_names)
    return data
