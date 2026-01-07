from typing import Set, Dict
from cookie_analyzer.core.schemas import Cookie, ConsentUI


def run_cookie_checks(
    cookies: list[Cookie],
    consent_ui: ConsentUI,
    site_domain: str,
    flags: Set[str],
    facts: Dict[str, object],
) -> None:
    """
    Run deterministic checks on cookie metadata.
    Populates flags and objective facts.
    """

    _check_third_party_cookies(cookies, site_domain, flags, facts)
    _check_long_retention(cookies, flags, facts)
    _check_tracking_enabled_by_default(consent_ui, flags)


def _check_third_party_cookies(
    cookies: list[Cookie],
    site_domain: str,
    flags: Set[str],
    facts: Dict[str, object],
) -> None:
    third_party_domains = set()

    for cookie in cookies:
        if site_domain not in cookie.domain:
            third_party_domains.add(cookie.domain)

    if third_party_domains:
        flags.add("third_party_cookie")
        facts["third_party_domains"] = sorted(third_party_domains)


def _check_long_retention(
    cookies: list[Cookie],
    flags: Set[str],
    facts: Dict[str, object],
) -> None:
    max_retention = 0

    for cookie in cookies:
        if cookie.expiry_days > max_retention:
            max_retention = cookie.expiry_days

    if max_retention > 180:
        flags.add("long_retention")
        facts["max_retention_days"] = max_retention


def _check_tracking_enabled_by_default(
    consent_ui: ConsentUI,
    flags: Set[str],
) -> None:
    for category in consent_ui.categories:
        label = category.label.lower()
        if label in {"analytics", "marketing"} and category.prechecked:
            flags.add("tracking_enabled_by_default")
            break
