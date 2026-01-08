from typing import Dict, Any, Set

from cookie_analyzer.core.schemas import CookieAnalyzerInput
from cookie_analyzer.rules.ui_rules import run_ui_checks
from cookie_analyzer.rules.cookie_rules import run_cookie_checks
from cookie_analyzer.rules.deception_rules import run_deception_checks


def analyze_cookie_usage(data: CookieAnalyzerInput) -> Dict[str, Any]:
    flags: Set[str] = set()
    facts: Dict[str, Any] = {}

    # 1. Consent UI checks
    run_ui_checks(
        consent_ui=data.consent_ui,
        flags=flags,
    )

    # 2. Cookie behavior checks
    run_cookie_checks(
        cookies=data.cookies,
        consent_ui=data.consent_ui,
        site_domain=data.site_domain,
        flags=flags,
        facts=facts,
    )

    # 3. Deception / misleading usage checks
    run_deception_checks(
        consent_ui=data.consent_ui,
        cookies=data.cookies,
        flags=flags,
        facts=facts,
    )

    # 4. Risk scoring
    risk_level = _compute_risk_level(flags)

    # 🔹 THIS IS THE IMPORTANT LINE
    summary = build_summary(flags, facts)

    return {
        "site_domain": data.site_domain,
        "risk_level": risk_level,
        "summary": summary,
        "flags": sorted(flags),
        "facts": facts,
    }



def _compute_risk_level(flags: Set[str]) -> str:
    count = len(flags)

    if count >= 5:
        return "high"
    if count >= 2:
        return "medium"
    return "low"
def build_summary(flags: Set[str], facts: Dict[str, Any]) -> str:
    if not flags:
        return "No significant cookie or consent risks were detected."

    lines = []

    if "third_party_cookie" in flags:
        domains = facts.get("third_party_domains", [])
        if domains:
            lines.append(
                f"Third-party cookies were detected from domains such as {', '.join(domains[:3])}."
            )
        else:
            lines.append("Third-party cookies were detected.")

    if "long_retention" in flags:
        days = facts.get("max_retention_days")
        if days:
            lines.append(
                f"Some cookies persist for up to {days} days, which may enable long-term tracking."
            )
        else:
            lines.append("Some cookies have long retention periods.")

    if "asymmetric_choice" in flags:
        lines.append(
            "Rejecting cookies requires more effort than accepting them, which may limit user choice."
        )

    if "prechecked_nonessential" in flags:
        lines.append(
            "Non-essential cookies are enabled by default without explicit user consent."
        )

    return " ".join(lines)
