from .types import clamp, Signals

def score_policy(signals: Signals, data_collected: list[str]):
    reasons = []
    score = 0

    def add(rule: str, delta: int):
        nonlocal score
        score += delta
        reasons.append({"rule": rule, "delta": delta})

    sensitivity = 0
    if any(x in data_collected for x in ["Email", "Phone"]):
        sensitivity += 1
    if any(x in data_collected for x in ["IP address", "Device info", "Cookies"]):
        sensitivity += 1
    if any(x in data_collected for x in ["Location", "Payment info"]):
        sensitivity += 2
    sensitivity = min(3, sensitivity)
    add("data_sensitivity", sensitivity)

    if signals["mentions_third_party_sharing"]:
        add("third_party_sharing", 3)

    if not signals["mentions_opt_out"]:
        add("opt_out_missing", 1)
    if not signals["mentions_deletion_right"]:
        add("deletion_right_unclear", 1)
    if signals.get("mentions_opt_out"):
        add("opt_out_present", -1)

    if signals.get("mentions_deletion_right"):
        add("deletion_right_present", -1)



    # Clamp 0–10
    score = clamp(score, 0, 10)

    level = "Low" if score <= 3 else ("Medium" if score <= 6 else "High")
    return score, level, reasons
