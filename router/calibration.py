from db.database import get_setting, set_setting, get_recent_weak_tier_stats, init_db

init_db()

DEFAULT_THRESHOLD = 0.4
MIN_THRESHOLD = 0.2      # never go below this - some skepticism is always healthy
MAX_THRESHOLD = 0.6      # never go above this - some quality floor must remain


MIN_SAMPLE_SIZE = 20        # need at least this many recent weak-tier decisions to act
HIGH_FALLBACK_RATE = 0.15   # if fallbacks happen more than 15% of the time, get pickier
LOW_FALLBACK_RATE = 0.03    # if fallbacks happen less than 3% of the time, relax a bit
STEP = 0.05                 # how big each nudge is


def get_current_threshold() -> float:
    """Read the threshold the system is currently using (from the
    database), or fall back to the original default if none is set yet."""
    value = get_setting("classifier_threshold", default=str(DEFAULT_THRESHOLD))
    return float(value)


def recalibrate_threshold(sample_limit: int = 50, verbose: bool = True) -> dict:
    """
    Look at recent history and decide whether to nudge the threshold.
    Returns a dict describing what happened (useful for the recalibrate.py
    script to print, and easy to unit-test without needing print output).
    """
    current = get_current_threshold()
    stats = get_recent_weak_tier_stats(limit=sample_limit)
 
    if stats["sample_size"] < MIN_SAMPLE_SIZE:
        result = {
            "action": "no_change",
            "reason": f"Not enough data yet ({stats['sample_size']}/{MIN_SAMPLE_SIZE} needed)",
            "old_threshold": current,
            "new_threshold": current,
            "fallback_rate": stats["fallback_rate"],
            "sample_size": stats["sample_size"],
        }
        if verbose:
            print(f"[calibration] {result['reason']} - threshold stays at {current}")
        return result
 
    fallback_rate = stats["fallback_rate"]
    new_threshold = current
    action = "no_change"
    reason = f"Fallback rate ({fallback_rate * 100:.1f}%) is within the healthy range"
 
    if fallback_rate > HIGH_FALLBACK_RATE:
        new_threshold = round(min(current - STEP, MAX_THRESHOLD), 2)
        new_threshold = max(new_threshold, MIN_THRESHOLD)
        action = "lowered"
        reason = (f"Fallback rate ({fallback_rate * 100:.1f}%) is too high - "
                   f"being pickier about what counts as 'easy'")
    elif fallback_rate < LOW_FALLBACK_RATE:
        new_threshold = round(min(current + STEP, MAX_THRESHOLD), 2)
        action = "raised"
        reason = (f"Fallback rate ({fallback_rate * 100:.1f}%) is very low - "
                   f"the cheap model is doing great, trusting it a bit more")
 
    if new_threshold != current:
        set_setting("classifier_threshold", new_threshold)
 
    result = {
        "action": action,
        "reason": reason,
        "old_threshold": current,
        "new_threshold": new_threshold,
        "fallback_rate": fallback_rate,
        "sample_size": stats["sample_size"],
    }
 
    if verbose:
        print(f"[calibration] {reason}")
        if action != "no_change":
            print(f"[calibration] Threshold {current} -> {new_threshold}")
        else:
            print(f"[calibration] Threshold stays at {current}")
 
    return result
