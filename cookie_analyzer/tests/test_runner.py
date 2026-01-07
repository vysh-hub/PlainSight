import json
import time
from pathlib import Path
from urllib.parse import urlparse

from cookie_analyzer.core.schemas import (
    Cookie,
    ConsentUI,
    CookieAnalyzerInput,
)
from cookie_analyzer.core.engine import analyze_cookie_usage


# -----------------------------
# Helper MUST come first
# -----------------------------
def compute_expiry_days(expiration_ts):
    """
    Convert browser expirationDate (unix timestamp)
    into number of days from now.
    """
    if not expiration_ts:
        return 0  # session or unknown

    now = int(time.time())
    seconds_left = int(expiration_ts) - now

    if seconds_left <= 0:
        return 0

    return seconds_left // (60 * 60 * 24)


def load_test_input() -> CookieAnalyzerInput:
    """
    Load extension-style test_input.json and adapt it
    into CookieAnalyzerInput expected by the engine.
    """

    test_file = Path(__file__).parent / "test_input.json"

    with open(test_file, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # 1. Parse site domain
    parsed_url = urlparse(raw["url"])
    site_domain = parsed_url.hostname or raw["url"]

    # 2. DOM cookies
    dom_cookies = raw["cookies"]["dom"]

    # 3. Browser cookies → Cookie objects
    cookies = []
    for c in raw["cookies"]["browser"]:
        cookies.append(
            Cookie(
                name=c["name"],
                domain=c["domain"],
                expiry_days=compute_expiry_days(c.get("expirationDate")),
                secure=c["secure"],
                sameSite=c["sameSite"],
            )
        )

    # 4. CMP info
    cmp_info = raw["cmp"]

    # 5. Mocked Consent UI
    consent_ui = ConsentUI(
        accept_clicks=0,
        reject_clicks=0,
        manage_preferences_visible=False,
        consent_required_to_proceed=False,
        categories=[],
    )

    return CookieAnalyzerInput(
        site_domain=site_domain,
        cookies=cookies,
        dom_cookies=dom_cookies,
        cmp_info=cmp_info,
        consent_ui=consent_ui,
    )


if __name__ == "__main__":
    data = load_test_input()
    result = analyze_cookie_usage(data)

    print("\n=== COOKIE ANALYZER RESULT ===\n")
    print(json.dumps(result, indent=2))
