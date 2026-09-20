from prometheus_client import Counter, Histogram

"""
- smartroute_requests_total       - how many questions routed, by tier
- smartroute_cost_usd_total        - running total cost, by tier
- smartroute_request_latency_seconds - how long requests take, by tier (as
                                          a histogram, so we can see the
                                          full spread, not just an average)
- smartroute_fallbacks_total         - how many times the quality
                                          fallback kicked in
"""

REQUESTS_TOTAL = Counter(
    "smartroute_requests_total",
    "Total number of routed requests",
    ["tier"],
)

COST_TOTAL = Counter(
    "smartroute_cost_usd_total",
    "Total estimated cost in USD",
    ["tier"],
)

REQUEST_LATENCY = Histogram(
    "smartroute_request_latency_seconds",
    "Request latency in seconds",
    ["tier"],
)

FALLBACKS_TOTAL = Counter(
    "smartroute_fallbacks_total",
    "Total number of quality-fallback triggers (weak model failed, retried on strong)",
)


def record_metrics(result: dict):
    """
    Update our dashboard gauges based on one completed routing decision.
    Wrapped defensively so a metrics hiccup can never break an actual
    user-facing request - same philosophy as our database logging.
    """
    try:
        tier = result["tier_used"]
        REQUESTS_TOTAL.labels(tier=tier).inc()
        COST_TOTAL.labels(tier=tier).inc(result["estimated_cost_usd"])
        REQUEST_LATENCY.labels(tier=tier).observe(result["latency_seconds"])
        if result["fallback_triggered"]:
            FALLBACKS_TOTAL.inc()
    except Exception as e:
        print(f"[warning] Failed to record Prometheus metrics: {e}")
