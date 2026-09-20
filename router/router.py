from router.classifier import classify_complexity
from router.cost_latency import apply_latency_adjustment
from router.model_registry import get_model, estimate_cost
from router.llm_clients import call_model
from db.database import init_db, log_decision
from metrics.prometheus_metrics import record_metrics


init_db()


def route_query(query: str, force_tier: str = None, agent: str = None, classify_on: str = None, min_useful_length: int = 10) -> dict:

    # Step 1: Classify the question. By default we classify whatever text
    # is actually being sent to the model (`query`) - but agent-team
    # prompts are usually the raw topic wrapped in instructions, research
    # notes, or a full draft to review, which is almost always long
    # enough to look "complex" regardless of how simple the topic itself
    # is. Passing classify_on lets a caller classify by the original
    # topic instead, while still sending the full wrapped prompt to
    # whichever model gets picked.
    classification = classify_complexity(classify_on if classify_on is not None else query)

    # Step 1b: Combined cost/latency objective - only reconsider the
    # decision when nothing was explicitly forced, since a forced tier is
    # an intentional override we should always respect as-is.
    if not force_tier:
        classification = apply_latency_adjustment(classification)

    tier = force_tier if force_tier else classification["tier"]

    # Step 2: Look up which model that tier means
    model_info = get_model(tier)

    # Step 3: Actually call the model
    result = call_model(model_info["provider"], model_info["name"], query)

    fallback_triggered = False
    # Default 10 characters assumes a normal-length answer is expected.
    # Callers asking for a deliberately short, direct answer (e.g. "just
    # give me the number") should pass a smaller min_useful_length, or a
    # correct-but-brief response like "4." will falsely look like the
    # weak tier failed and trigger an unnecessary strong-tier retry.
    if tier == "weak" and len(result["answer"].strip()) < min_useful_length:
        fallback_triggered = True
        tier = "strong"
        model_info = get_model(tier)
        result = call_model(model_info["provider"], model_info["name"], query)

    # Step 4: Work out the (rough) cost
    cost = estimate_cost(tier, result["input_tokens"], result["output_tokens"])

    # Step 5: Package everything up so the caller (UI, eval script, etc.)
    # has full visibility into what happened and WHY.
    final_result = {
        "query": query,
        "answer": result["answer"],
        "tier_used": tier,
        "model_used": model_info["name"],
        "provider": model_info["provider"],
        "complexity_score": classification["score"],
        "threshold": classification["threshold"],
        "reasons": classification["reasons"],
        "was_forced": force_tier is not None,
        "latency_override": classification.get("latency_override", False),
        "fallback_triggered": fallback_triggered,
        "latency_seconds": result["latency_seconds"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "estimated_cost_usd": cost,
    }

    log_decision(query, final_result, agent=agent)
    record_metrics(final_result)
    return final_result
