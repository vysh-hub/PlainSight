from typing import Dict, Any, Set, List

from cookie_analyzer.core.schemas import CookieAnalyzerInput
from cookie_analyzer.rules.ui_rules import run_ui_checks
from cookie_analyzer.rules.cookie_rules import run_cookie_checks
from cookie_analyzer.rules.deception_rules import run_deception_checks
from cookie_analyzer.rules.consent_rules import (
    detect_pre_consent_tracking,
    detect_user_profiling_identifiers,
    detect_non_standard_consent_signals,
)
def _build_cookie_stats(cookies):
    total = len(cookies)
    session = sum(1 for c in cookies if getattr(c, "session", False))
    persistent = total - session

    return {
        "total": total,
        "session": session,
        "persistent": persistent,
    }


def _build_evidence(consent_flags):
    return list(
        {f.get("cookie") for f in consent_flags if f.get("cookie")}
    )


def _build_summary(risk_level, flags):
    if risk_level == "high":
        return (
            "This site exhibits multiple high-risk privacy behaviors, "
            "including tracking or profiling cookies without clear consent."
        )
    if risk_level == "medium":
        return (
            "This site shows potential privacy concerns that may affect user consent or data usage."
        )
    return "No significant privacy risks were detected based on observed cookie behavior."



def analyze_cookie_usage(data: CookieAnalyzerInput) -> Dict[str, Any]:
    """
    Main orchestration function.
    Runs all deterministic checks and returns structured findings.
    This is the PRIMARY entry point for the browser extension.
    """

    flags: Set[str] = set()
    facts: Dict[str, Any] = {}

    # -----------------------------
    # 1. Consent UI checks
    # -----------------------------
    run_ui_checks(
        consent_ui=data.consent_ui,
        flags=flags,
    )

    # -----------------------------
    # 2. Cookie behavior checks
    # -----------------------------
    run_cookie_checks(
        cookies=data.cookies,
        consent_ui=data.consent_ui,
        site_domain=data.site_domain,
        flags=flags,
        facts=facts,
    )

    # -----------------------------
    # 3. Deception / misleading usage checks
    # -----------------------------
    run_deception_checks(
        consent_ui=data.consent_ui,
        cookies=data.cookies,
        flags=flags,
        facts=facts,
    )

    # -----------------------------
    # 4. Consent framework analysis (NEW)
    # -----------------------------
    consent_flags: List[Dict[str, Any]] = []

    consent_flags.extend(
        detect_pre_consent_tracking(
            dom_cookies=data.dom_cookies,
            cmp_info=data.cmp_info,
        )
    )

    consent_flags.extend(
        detect_user_profiling_identifiers(
            cookies=data.cookies
        )
    )

    consent_flags.extend(
        detect_non_standard_consent_signals(
            cookies=data.cookies,
            cmp_info=data.cmp_info,
        )
    )

    # Merge consent flags into global flag set
    for f in consent_flags:
        flags.add(f["type"])

    # -----------------------------
    # 5. Risk scoring (deterministic)
    # -----------------------------
    risk_level = _compute_risk_level(flags)

    # -----------------------------
    # 6. Final structured response
    # -----------------------------
    cookie_stats = _build_cookie_stats(data.cookies)
    evidence = _build_evidence(consent_flags)
    summary = _build_summary(risk_level, flags)

    return {
        "url": data.site_domain,
        "summary": summary,
        "risk_level": risk_level,
        "flags": sorted(flags),
        "cookie_stats": cookie_stats,
        "evidence": evidence,
        "consent_analysis": {
            "cmp_detected": data.cmp_info.get("detected", {}),
            "providers": data.cmp_info.get("providers", {}),
            "flags": consent_flags,
        },
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
