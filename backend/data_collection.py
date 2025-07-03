from pymongo import MongoClient
from datetime import datetime
import os
from typing import List, Dict, Any

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["mood_tracker"]
collection = db["mood_entries"]

def add_mood_entry(data: Dict[str, Any]) -> None:
    """Add a mood entry to the database."""
    # Basic validation
    data["timestamp"] = data.get("timestamp") or datetime.utcnow().isoformat()
    data["mood_score"] = int(data["mood_score"])
    collection.insert_one(data)

def get_mood_entries() -> List[Dict[str, Any]]:
    """Retrieve all mood entries from the database."""
    return list(collection.find({}, {"_id": 0})) 