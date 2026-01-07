from .types import PolicyInput
from .clean import clean_text
from .section import split_into_sections
from .signals import extract_signals, extract_data_collected
from .score import score_policy
from .takeaways import build_takeaways
from .openrouter_client import openrouter_write_takeaways
from .risk_labels import risks_and_red_flags


def run_policy_pipeline(inp: PolicyInput) -> dict:
    cleaned = clean_text(inp.raw_text)
    sections = split_into_sections(cleaned)

    is_policy_page = any(k in (inp.url or "").lower() for k in ["privacy", "terms", "legal", "cookie"])

    signals = extract_signals(sections)
    data_collected = extract_data_collected(cleaned)

    score, level, reasons = score_policy(signals, data_collected)

    key_takeaways, summary_simple = build_takeaways(signals, data_collected)
    risks, red_flags = risks_and_red_flags(signals)

    llm = openrouter_write_takeaways(cleaned)

    if isinstance(llm, dict):
        summary_simple = llm.get("summary_simple", summary_simple)
        key_takeaways = llm.get("key_takeaways", key_takeaways)
        risks = llm.get("risks", risks)
        red_flags = llm.get("red_flags", red_flags)




    return {
        "url": inp.url,
        "title": inp.title,
        "is_policy_page": is_policy_page,
        "summary_simple": summary_simple,
        "key_takeaways": key_takeaways,
        "risks": risks,
        "red_flags": red_flags,
        "policy_risk_score": score,
        "risk_level": level,
        "captured_at": inp.captured_at,
    }
