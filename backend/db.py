from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client["Polocies_tracker"]

policies_col = db["polocies"]
cookies_col = db["cookies"]


def save_policy(url: str, text: str):
    policies_col.insert_one({
        "url": url,
        "text": text,
        "created_at": datetime.utcnow()
    })


def save_cookie(domain: str, result: dict):
    cookies_col.insert_one({
        "type": "cookie",
        "domain": domain,
        "result": result,
        "created_at": datetime.utcnow()
    })


def get_policies(limit: int = 50):
    data = []
    for p in policies_col.find().sort("created_at", -1).limit(limit):
        p["_id"] = str(p["_id"])
        data.append(p)
    return data
