from db.database import get_summary_stats


LATENCY_MARGIN_MULTIPLIER = 1.5
BORDERLINE_BAND = 0.10


def apply_latency_adjustment(classification: dict) -> dict:
    classification = dict(classification)
    classification.setdefault("latency_override", False)

    if classification["tier"] != "weak":
        return classification
    

    stats = get_summary_stats()
    weak_latency = stats.get("avg_latency_weak")
    strong_latency = stats.get("avg_latency_strong")


    if not weak_latency or not strong_latency:
        return classification


    score = classification["score"]
    threshold = classification["threshold"]
    is_broderline = (threshold - score) <= BORDERLINE_BAND
    weak_is_meaningfully_slower = weak_latency > (strong_latency * LATENCY_MARGIN_MULTIPLIER)


    if is_broderline and weak_is_meaningfully_slower:
        classification["tier"] = "strong"
        classification["latency_override"] = True
        classification["reasons"] = classification["reasons"] + [
            f"Latency override: weak tier averaging {weak_latency}s vs "
            f"strong tier {strong_latency}s recently - broderline "
            f"complexity ({score} near threshold {threshold}), so the "
            f"'cheap' tier isn't actually the faster option right now."
        ]
        
    return classification


    
