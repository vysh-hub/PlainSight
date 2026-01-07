import re
from .types import Signals, PolicySections

DATA_PATTERNS = [
    ("Email", r"\bemail\b"),
    ("Phone", r"\bphone\b|\bmobile\b"),
    ("IP address", r"\bip address\b"),
    ("Location", r"\blocation\b|\bgps\b"),
    ("Payment info", r"\bcredit card\b|\bdebit\b|\bpayment\b"),
    ("Device info", r"\bdevice\b|\buser agent\b|\bbrowser\b"),
    ("Cookies", r"\bcookie\b"),
]

def extract_data_collected(text: str):
    low = text.lower()
    found = []
    for label, pat in DATA_PATTERNS:
        if re.search(pat, low):
            found.append(label)
    return sorted(set(found))

def extract_signals(sections: PolicySections) -> Signals:
    full = "\n".join(sections.values()).lower()

    return {
        "mentions_tracking": bool(re.search(r"(track|tracking|analytics|advertis)", full)),
        "mentions_third_party_sharing": bool(re.search(r"(third party|share(d)? with|partners|advertis|service provider)", full)),
        "mentions_sale_of_data": bool(re.search(r"\bsell\b|\bsale of\b", full)),
        "mentions_retention_limit": bool(re.search(r"(retain.*\d+ (day|month|year)s?|retention period|we keep.*\d+)", full)),
        "mentions_opt_out": bool(re.search(r"(opt[- ]out|withdraw consent|unsubscribe|do not sell)", full)),
        "mentions_deletion_right": bool(re.search(r"(delete your data|right to delete|erasure)", full)),
    }
