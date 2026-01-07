from typing import Set, Dict
from cookie_analyzer.core.schemas import ConsentUI, Cookie


def run_deception_checks(
    consent_ui: ConsentUI,
    cookies: list[Cookie],
    flags: Set[str],
    facts: Dict[str, object],
) -> None:
    """
    Detect misleading or deceptive consent practices by
    cross-checking UI claims against actual behavior.
    """

    _check_misleading_essential_claim(consent_ui, flags)
    _check_category_behavior_mismatch(consent_ui, cookies, flags, facts)
    _check_preconsent_tracking(cookies, flags)


def _check_misleading_essential_claim(
    consent_ui: ConsentUI,
    flags: Set[str],
) -> None:
    """
    Flag if the UI implies only essential cookies are used,
    but non-essential categories are enabled.
    """
    claims_essential_only = any(
        "essential" in category.description.lower()
        for category in consent_ui.categories
    )

    nonessential_enabled = any(
        category.label.lower() in {"analytics", "marketing"}
        and category.prechecked
        for category in consent_ui.categories
    )

    if claims_essential_only and nonessential_enabled:
        flags.add("misleading_claim")


def _check_category_behavior_mismatch(
    consent_ui: ConsentUI,
    cookies: list[Cookie],
    flags: Set[str],
    facts: Dict[str, object],
) -> None:
    """
    Flag if analytics-labeled categories include
    obvious third-party advertising cookies.
    """
    analytics_enabled = any(
        category.label.lower() == "analytics" and category.prechecked
        for category in consent_ui.categories
    )

    third_party_present = any(
        "." in cookie.domain for cookie in cookies
    )

    if analytics_enabled and third_party_present:
        flags.add("category_mismatch")
        facts["category_mismatch_reason"] = (
            "Analytics category includes third-party tracking cookies"
        )


def _check_preconsent_tracking(
    cookies: list[Cookie],
    flags: Set[str],
) -> None:
    """
    Placeholder: flag if cookies exist before consent.
    Currently inferred from presence of non-essential cookies.
    """
    if cookies:
        flags.add("potential_preconsent_tracking")
