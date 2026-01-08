import os
import sys
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Make sure Python can import your policy package ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # PlainSight/
POLICY_SRC = os.path.join(ROOT, "policy", "src")
if POLICY_SRC not in sys.path:
    sys.path.insert(0, POLICY_SRC)

# Now we can import your pipeline
from pipeline.run_pipeline import run_policy_pipeline  # type: ignore
from pipeline.types import PolicyInput  # type: ignore

app = FastAPI()

# TEMP for hackathon/dev: allow all. Later restrict to chrome-extension://<id>
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PolicyReq(BaseModel):
    url: str
    title: str = ""
    raw_text: str
    captured_at: Optional[str] = None

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/policy/analyze")
def analyze(req: PolicyReq):
    inp = PolicyInput(
        url=req.url,
        title=req.title,
        raw_text=req.raw_text,
        captured_at=req.captured_at
    )

    out = run_policy_pipeline(inp)

    # Return only what the side panel needs (stable contract)
    return {       
        "summary_simple": out.get("summary_simple", ""),
        "key_takeaways": out.get("key_takeaways", []),

        "policy_risk_score": out.get("policy_risk_score", 0),
        "risk_level": out.get("risk_level", "Low"),
    }
