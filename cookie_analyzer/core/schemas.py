from typing import List
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Cookie:
    name: str
    domain: str
    expiry_days: int
    secure: bool
    sameSite: str


@dataclass
class Category:
    label: str
    description: str
    prechecked: bool


@dataclass
class ConsentUI:
    accept_clicks: int
    reject_clicks: int
    manage_preferences_visible: bool
    consent_required_to_proceed: bool
    categories: List[Category]

@dataclass
class CookieAnalyzerInput:
    site_domain: str
    cookies: List[Any]              # Browser cookies (normalized)
    dom_cookies: List[Dict[str, Any]]
    cmp_info: Dict[str, Any]
    consent_ui: Any