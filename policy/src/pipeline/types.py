from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class PolicyInput:
    url: str
    title: str
    raw_text: str
    captured_at: Optional[str] = None

PolicySections = Dict[str, str]
Signals = Dict[str, bool]

def clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))
