from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


# MongoDB connection
MONGO_URI = "mongodb://localhost:xxxxx/Pxxxxxxxxxxker"
client = MongoClient(MONGO_URI)
db = client["Polocies_tracker"]
policies = db["polocies"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PolicyPayload(BaseModel):
    url: str
    text: str

@app.post("/save-policy")
def save_policy(data: PolicyPayload):
    document = {
        "url": data.url,
        "text": data.text,
        "created_at": datetime.utcnow()
    }
    policies.insert_one(document)
    return {"status": "saved"}
from bson import ObjectId

@app.get("/policies")
def get_policies():
    data = []
    for p in policies.find().sort("created_at", -1).limit(50):
        p["_id"] = str(p["_id"])
        data.append(p)
    return data
