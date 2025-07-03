import pandas as pd
from scipy.stats import zscore
from backend.data_collection import get_mood_entries
import numpy as np
from sklearn.cluster import KMeans
from typing import Dict, Any

def detect_patterns() -> Dict[str, Any]:
    """Detects mood patterns, anomalies, clusters, and returns last 7 days' moods."""
    entries = get_mood_entries()
    if not entries:
        return {}
    df = pd.DataFrame(entries)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df["zscore"] = zscore(df["mood_score"])
    anomalies = df[df["zscore"].abs() > 2]["timestamp"].dt.strftime("%Y-%m-%d").tolist()
    # Recurring low moods (e.g., Mondays)
    df["weekday"] = df["timestamp"].dt.day_name()
    low_mood_days = df[df["mood_score"] <= 3]["weekday"].value_counts().to_dict()
    # --- Clustering: Group days by mood patterns ---
    # Features: mood_score, (optionally add more features like tags count, etc.)
    X = df[["mood_score"]].values
    n_clusters = min(3, len(df)) if len(df) > 1 else 1
    if len(df) > 1:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df["cluster"] = kmeans.fit_predict(X)
        cluster_centers = kmeans.cluster_centers_.flatten().tolist()
        clusters = df[["timestamp", "mood_score", "cluster"]].to_dict(orient="records")
    else:
        df["cluster"] = 0
        cluster_centers = [df["mood_score"].iloc[0]]
        clusters = df[["timestamp", "mood_score", "cluster"]].to_dict(orient="records")
    # --- Last 7 days' moods ---
    last_7_days = df.sort_values("timestamp", ascending=False).head(7)[["timestamp", "mood_score", "cluster"]]
    last_7_days = last_7_days.sort_values("timestamp").to_dict(orient="records")
    return {
        "anomalies": anomalies,
        "low_mood_days": low_mood_days,
        "clusters": clusters,
        "cluster_centers": cluster_centers,
        "last_7_days": last_7_days
    } 