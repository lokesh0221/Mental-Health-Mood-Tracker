from fastapi import FastAPI, HTTPException
from backend.data_collection import add_mood_entry, get_mood_entries
from backend.sentiment_analysis import analyze_sentiment
from backend.trend_analysis import get_trends
from backend.pattern_detection import detect_patterns
from backend.recommendation import get_recommendations

app = FastAPI()

@app.post("/mood_entry")
def mood_entry(data: dict):
    sentiment = analyze_sentiment(data.get("journal_text", ""))
    data["sentiment"] = sentiment
    add_mood_entry(data)
    return {"status": "success"}

@app.get("/mood_entries")
def mood_entries():
    return get_mood_entries()

@app.get("/trends")
def trends():
    return get_trends()

@app.get("/patterns")
def patterns():
    return detect_patterns()

@app.get("/recommendations")
def recommendations():
    return get_recommendations() 