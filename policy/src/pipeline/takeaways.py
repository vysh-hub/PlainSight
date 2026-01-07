from .types import Signals

def build_takeaways(signals: Signals, data_collected: list[str]):
    takeaways = []

    if data_collected:
        takeaways.append(f"Collects data such as: {', '.join(data_collected)}.")
    else:
        takeaways.append("The policy describes collecting personal and/or device information, but details may be unclear.")

    if signals["mentions_third_party_sharing"]:
        takeaways.append("Mentions sharing data with third parties (such as partners, advertisers, or service providers).")
    else:
        takeaways.append("Does not clearly mention third-party sharing (may still occur—verify details).")

    if signals["mentions_tracking"]:
        takeaways.append("Mentions tracking/analytics/cookies for measurement or advertising.")
    else:
        takeaways.append("Does not clearly mention tracking/analytics/cookies.")

    if not signals["mentions_retention_limit"]:
        takeaways.append("Retention duration is unclear or not explicitly limited.")
    else:
        takeaways.append("Mentions a defined retention duration or retention policy.")

    if not signals["mentions_opt_out"]:
        takeaways.append("Opt-out/withdrawal options are not clearly described.")
    else:
        takeaways.append("Mentions opt-out or consent withdrawal options.")

    if not signals["mentions_deletion_right"]:
        takeaways.append("Deletion/erasure rights are not clearly described.")
    else:
        takeaways.append("Mentions deletion/erasure rights.")

    summary = " ".join(takeaways[:3])
    return takeaways[:6], summary
