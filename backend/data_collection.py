from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["mood_tracker"]
collection = db["mood_entries"]

def add_mood_entry(data):
    # Basic validation
    data["timestamp"] = data.get("timestamp") or datetime.utcnow().isoformat()
    data["mood_score"] = int(data["mood_score"])
    collection.insert_one(data)

def get_mood_entries():
    return list(collection.find({}, {"_id": 0})) 