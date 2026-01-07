from typing import Set
from cookie_analyzer.core.schemas import ConsentUI


def run_ui_checks(consent_ui: ConsentUI, flags: Set[str]) -> None:
    """
    Run deterministic checks on the consent UI structure.
    Mutates the flags set in-place.
    """

    _check_asymmetric_choice(consent_ui, flags)
    _check_forced_consent(consent_ui, flags)
    _check_hidden_preferences(consent_ui, flags)
    _check_prechecked_nonessential(consent_ui, flags)


def _check_asymmetric_choice(consent_ui: ConsentUI, flags: Set[str]) -> None:
    """
    Flag if rejecting cookies requires more user effort than accepting.
    """
    if consent_ui.accept_clicks < consent_ui.reject_clicks:
        flags.add("asymmetric_choice")


def _check_forced_consent(consent_ui: ConsentUI, flags: Set[str]) -> None:
    """
    Flag if consent is required to proceed on the site.
    """
    if consent_ui.consent_required_to_proceed:
        flags.add("forced_consent")


def _check_hidden_preferences(consent_ui: ConsentUI, flags: Set[str]) -> None:
    """
    Flag if users cannot easily access cookie preferences.
    """
    if not consent_ui.manage_preferences_visible:
        flags.add("hidden_preferences")


def _check_prechecked_nonessential(consent_ui: ConsentUI, flags: Set[str]) -> None:
    """
    Flag if non-essential categories (analytics/marketing) are pre-enabled.
    """
    for category in consent_ui.categories:
        label = category.label.lower()
        if label in {"analytics", "marketing"} and category.prechecked:
            flags.add("prechecked_nonessential")
