import json
from pathlib import Path

from cookie_analyzer.core.schemas import (
    Cookie,
    Category,
    ConsentUI,
    CookieAnalyzerInput,
)
from cookie_analyzer.core.engine import analyze_cookie_usage


def load_test_input() -> CookieAnalyzerInput:
    """
    Load test_input.json and convert it into CookieAnalyzerInput.
    """

    test_file = Path(__file__).parent / "test_input.json"

    with open(test_file, "r", encoding="utf-8") as f:
        raw = json.load(f)

    cookies = [
        Cookie(**cookie)
        for cookie in raw["cookies"]
    ]

    categories = [
        Category(**category)
        for category in raw["consent_ui"]["categories"]
    ]

    consent_ui = ConsentUI(
        accept_clicks=raw["consent_ui"]["accept_clicks"],
        reject_clicks=raw["consent_ui"]["reject_clicks"],
        manage_preferences_visible=raw["consent_ui"]["manage_preferences_visible"],
        consent_required_to_proceed=raw["consent_ui"]["consent_required_to_proceed"],
        categories=categories,
    )

    return CookieAnalyzerInput(
        site_domain=raw["site_domain"],
        cookies=cookies,
        consent_ui=consent_ui,
        cmp_detected=raw["cmp_detected"],
    )


if __name__ == "__main__":
    data = load_test_input()
    result = analyze_cookie_usage(data)

    print("\n=== COOKIE ANALYZER RESULT ===")
    print(f"Risk Level: {result['risk_level']}")
    print("\nFlags:")
    for flag in result["flags"]:
        print(f" - {flag}")

    print("\nFacts:")
    for key, value in result["facts"].items():
        print(f" - {key}: {value}")
