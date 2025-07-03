import pandas as pd
from backend.data_collection import get_mood_entries
from typing import Dict, Any

def get_trends() -> Dict[str, Any]:
    """Return mood trends including rolling mean for the last 7 days."""
    entries = get_mood_entries()
    if not entries:
        return {}
    df = pd.DataFrame(entries)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df["rolling_mean"] = df["mood_score"].rolling(window=7, min_periods=1).mean()
    return {
        "dates": df["timestamp"].dt.strftime("%Y-%m-%d").tolist(),
        "mood_scores": df["mood_score"].tolist(),
        "rolling_mean": df["rolling_mean"].tolist()
    } 