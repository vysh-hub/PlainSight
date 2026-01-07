import re
from typing import List, Dict

# --- heuristics ---
UUID_REGEX = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
    re.IGNORECASE,
)

BASE64_REGEX = re.compile(r"^[A-Za-z0-9+/=]{20,}$")


def is_non_essential(cookie_name: str) -> bool:
    """Basic allowlist-style exclusion for essential cookies"""
    essential_keywords = ["session", "csrf", "xsrf", "auth"]
    return not any(k in cookie_name.lower() for k in essential_keywords)


def detect_pre_consent_tracking(dom_cookies: List[Dict], cmp_info: Dict):
    flags = []

    consent_given = any(cmp_info.get("detected", {}).values())
    if consent_given:
        return flags

    for c in dom_cookies:
        if is_non_essential(c["name"]):
            flags.append({
                "type": "PRE_CONSENT_TRACKING",
                "severity": "HIGH",
                "cookie": c["name"],
                "description": "Non-essential cookie set before any consent signal"
            })

    return flags


def detect_user_profiling_identifiers(cookies):
    flags = []

    for c in cookies:
        # Support both dict-based and dataclass-based cookies
        if isinstance(c, dict):
            name = c.get("name", "")
            value = str(c.get("value", ""))
        else:
            name = c.name
            value = ""  # Browser cookies may not expose value

        if UUID_REGEX.match(value) or BASE64_REGEX.match(value) or len(value) > 40:
            flags.append({
                "type": "USER_PROFILING_IDENTIFIER",
                "severity": "HIGH",
                "cookie": name,
                "description": "Cookie value resembles a persistent user identifier"
            })

    return flags


def detect_non_standard_consent_signals(cookies, cmp_info):
    flags = []

    standard_cmp_present = any(cmp_info.get("providers", {}).values()) or any(
        cmp_info.get("detected", {}).values()
    )

    # If a proper CMP exists, don't flag
    if standard_cmp_present:
        return flags

    consent_like_cookies = {
        "ckns_policy",
        "ckns_explicit",
        "_pprv",
    }

    for c in cookies:
        # Support both dict and Cookie dataclass
        if isinstance(c, dict):
            name = c.get("name", "")
        else:
            name = c.name

        if name in consent_like_cookies:
            flags.append({
                "type": "NON_STANDARD_CONSENT_SIGNAL",
                "severity": "MEDIUM",
                "cookie": name,
                "description": "Consent-like cookie present without recognized CMP framework"
            })

    return flags

