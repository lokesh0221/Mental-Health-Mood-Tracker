import pandas as pd
from scipy.stats import zscore
from backend.data_collection import get_mood_entries

def detect_patterns():
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
    return {"anomalies": anomalies, "low_mood_days": low_mood_days} 