from router.router import route_query

SAMPLE_QUERIES = [
    "Hi there!",
    "What is the capital of France?",
    "Define photosynthesis.",
    "Compare the economic policies of the US and China and analyze the "
    "trade-offs of each approach for a developing nation.",
    "Write a Python function that checks if a number is prime, and explain "
    "step by step how it works.",
    "What's 12 + 15?",
    "Can you explain in detail the architecture trade-offs between "
    "microservices and monoliths, and design a migration strategy?",
]


def main():
    print("-" * 70)
    print("SmartRoute-MCP - Router Demo")
    print("=" * 70)

    total_cost = 0.0

    for i, query in enumerate(SAMPLE_QUERIES, 1):
        print(f"\n[{i}] Query: {query}")
        result = route_query(query)

        print(f"    → Routed to: {result['tier_used'].upper()} "
              f"({result['provider']} / {result['model_used']})")
        print(f"    → Complexity score: {result['complexity_score']} "
              f"(threshold: {result['threshold']})")
        print(f"    → Why: {result['reasons']}")
        print(f"    → Latency: {result['latency_seconds']}s | "
              f"Cost: ${result['estimated_cost_usd']:.8f}")
        print(f"    → Answer preview: {result['answer'][:120]}"
              f"{'...' if len(result['answer']) > 120 else ''}")

        total_cost += result["estimated_cost_usd"]

        print("\n" + "-" * 70)
        print(f"Total estimated cost for {len(SAMPLE_QUERIES)} queries: "
              f"${total_cost:.8f}")
        print("(Compare this to what it would cost if EVERY query went to the "
              "strong model - we'll build that comparison property in Phase 9.)")
        print("=" * 70)

if __name__ == "__main__":
    main()
