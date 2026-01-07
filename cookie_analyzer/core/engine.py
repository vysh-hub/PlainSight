from typing import Dict, Any, Set

from cookie_analyzer.core.schemas import CookieAnalyzerInput
from cookie_analyzer.rules.ui_rules import run_ui_checks
from cookie_analyzer.rules.cookie_rules import run_cookie_checks
from cookie_analyzer.rules.deception_rules import run_deception_checks



def analyze_cookie_usage(data: CookieAnalyzerInput) -> Dict[str, Any]:
    """
    Main orchestration function.
    Runs all deterministic checks and returns structured findings.
    """

    flags: Set[str] = set()
    facts: Dict[str, Any] = {}

    # 1. Consent UI checks
    run_ui_checks(data.consent_ui, flags)

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

    # 4. Risk scoring (simple, explainable)
    risk_level = _compute_risk_level(flags)

    return {
        "risk_level": risk_level,
        "flags": sorted(flags),
        "facts": facts,
    }


def _compute_risk_level(flags: Set[str]) -> str:
    """
    Compute overall risk level based on number of flags.
    Deterministic and explainable.
    """
    count = len(flags)

    if count >= 5:
        return "high"
    if count >= 2:
        return "medium"
    return "low"
