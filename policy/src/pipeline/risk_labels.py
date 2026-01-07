from .types import Signals

def risks_and_red_flags(signals: Signals):
    risks = []
    red_flags = []

    if signals.get("mentions_third_party_sharing"):
        risks.append("Data may be shared with third parties (partners/advertisers/service providers).")

    if signals.get("mentions_tracking"):
        risks.append("Tracking/analytics cookies may be used for measurement or advertising.")

    if signals.get("mentions_sale_of_data"):
        red_flags.append("Policy mentions selling data (verify conditions).")

    if not signals.get("mentions_retention_limit", False):
        red_flags.append("Retention duration is unclear or open-ended.")

    if not signals.get("mentions_opt_out", False):
        red_flags.append("Opt-out/consent withdrawal is not clearly described.")

    if not signals.get("mentions_deletion_right", False):
        red_flags.append("Deletion/erasure rights are not clearly described.")

    return risks, red_flags
