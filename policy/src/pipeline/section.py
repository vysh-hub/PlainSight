import re
from .types import PolicySections

SECTION_MAP = {
    "data_collection": [r"collect", r"information we collect", r"data we collect", r"personal data"],
    "data_usage": [r"how we use", r"we use", r"purpose", r"processing"],
    "third_party_sharing": [r"share", r"third party", r"partners", r"advertis", r"service provider"],
    "retention": [r"retain", r"retention", r"store", r"keep your data"],
    "user_rights": [r"your rights", r"access", r"delete", r"opt[- ]out", r"withdraw consent"],
    "cookies_tracking": [r"cookie", r"tracking", r"analytics", r"advertising cookies"],
    "security": [r"security", r"protect", r"encryption", r"safeguard"],
}

def split_into_sections(cleaned: str) -> PolicySections:
    chunks = [c.strip() for c in cleaned.split("\n\n") if c.strip()]
    out: PolicySections = {}
    out["other"] = ""

    for ch in chunks:
        ch_low = ch.lower()
        best = "other"
        best_score = 0

        for sec, pats in SECTION_MAP.items():
            score = 0
            for p in pats:
                if re.search(p, ch_low):
                    score += 1
            if score > best_score:
                best_score = score
                best = sec

        out[best] = (out.get(best, "") + ch + "\n\n").strip()
    # remove empty
    return {k: v for k, v in out.items() if v.strip()}
