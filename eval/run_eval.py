import time
import json
import os
from datetime import datetime

from router.router import route_query
from eval.eval_questions import ALL_QUESTIONS


RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "eval_results")


def run_group(questions: list, force_tier: str = None, label: str = "") -> dict:
    """
    Run every question through route_query(), either letting the router
    decide (force_tier=None) or forcing everything to one tier.
    Returns a summary plus the raw per-question results.
    """

    results = []
    total_cost = 0.0
    total_latency = 0.0
    tier_counts = {"weak": 0, "strong": 0}
    fallback_count = 0


    print(f"\nRunning group: {label} ({len(questions)} questions)...")

    for i, q in enumerate(questions, 1):
        try:
            result = route_query(q, force_tier=force_tier)
        except Exception as e:
            # If a single question fails (e.g. a transient network hiccup),
            # don't let it kill the whole 100-question run - record the
            # failure and move on, like a survey that notes "no response"
            # for one participant instead of throwing out the whole study.
            print(f"  [{i}/{len(questions)}] FAILED: {e}")
            results.append({"query": q, "error": str(e)})
            continue
 
        total_cost += result["estimated_cost_usd"]
        total_latency += result["latency_seconds"]
        tier_counts[result["tier_used"]] = tier_counts.get(result["tier_used"], 0) + 1
        if result["fallback_triggered"]:
            fallback_count += 1
 
        results.append(result)
 
        if i % 10 == 0:
            print(f"  [{i}/{len(questions)}] done so far... "
                  f"(running cost: ${total_cost:.6f})")
 
    return {
        "label": label,
        "total_questions": len(questions),
        "total_cost_usd": round(total_cost, 8),
        "total_latency_seconds": round(total_latency, 2),
        "avg_latency_seconds": round(total_latency / len(questions), 2) if questions else 0,
        "tier_counts": tier_counts,
        "fallback_count": fallback_count,
        "results": results,
    }


def print_report(routed: dict, always_strong: dict):
    print("\n" + "=" * 70)
    print("SmartRoute-MCP — Evaluation Report")
    print("=" * 70)
 
    print(f"\n{'Metric':<30}{'Routed':<20}{'Always-Strong':<20}")
    print("-" * 70)
    print(f"{'Total questions':<30}{routed['total_questions']:<20}{always_strong['total_questions']:<20}")
    print(f"{'Total cost (USD)':<30}${routed['total_cost_usd']:<19.6f}${always_strong['total_cost_usd']:<19.6f}")
    print(f"{'Total time (seconds)':<30}{routed['total_latency_seconds']:<20}{always_strong['total_latency_seconds']:<20}")
    print(f"{'Avg latency/question (s)':<30}{routed['avg_latency_seconds']:<20}{always_strong['avg_latency_seconds']:<20}")
    print(f"{'Fallbacks triggered':<30}{routed['fallback_count']:<20}{always_strong['fallback_count']:<20}")
 
    print(f"\n{'Routed tier split:':<30}{routed['tier_counts']}")
 
    if always_strong["total_cost_usd"] > 0:
        savings_pct = (1 - routed["total_cost_usd"] / always_strong["total_cost_usd"]) * 100
    else:
        savings_pct = 0.0
 
    print("\n" + "-" * 70)
    print(f"COST SAVINGS FROM ROUTING: {savings_pct:.1f}%")
    print(f"(Routed cost ${routed['total_cost_usd']:.6f} vs. "
          f"Always-Strong cost ${always_strong['total_cost_usd']:.6f})")
    print("-" * 70)
 
    print("\nNOTE ON QUALITY: this script measures COST and SPEED precisely, "
          "since those are objective numbers. Judging ANSWER QUALITY "
          "automatically is a much harder problem (that's basically asking "
          "an AI to grade another AI's homework). For a real quality check, "
          "open eval_results/latest_report.json and manually spot-check a "
          "handful of 'weak' tier answers against their 'strong' tier "
          "equivalents for the same question - see if the cheap model's "
          "answers still feel 'good enough' for easy questions.")
    print("=" * 70)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
 
    questions = ALL_QUESTIONS
 
    start = time.time()
 
    routed = run_group(questions, force_tier=None, label="Routed (our system)")
    always_strong = run_group(questions, force_tier="strong", label="Always-Strong (control group)")
 
    elapsed = time.time() - start
 
    print_report(routed, always_strong)
    print(f"\nTotal evaluation wall-clock time: {elapsed / 60:.1f} minutes")
 
    # Save the full raw results so we can inspect individual answers later.
    report = {
        "generated_at": datetime.now().isoformat(),
        "routed": routed,
        "always_strong": always_strong,
    }
    out_path = os.path.join(RESULTS_DIR, "latest_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
 
    print(f"\nFull results saved to: {out_path}")
 
 
if __name__ == "__main__":
    main()
