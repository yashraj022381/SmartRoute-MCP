from db.database import get_summary_stats

def main():
    stats = get_summary_stats()

    print("=" * 60)
    print("SmartRoute-MCP - Performance Summary")
    print("=" * 60)

    if stats["total_queries"] == 0:
        print("\nNo data yet! Run test_router.py or test_agents.py first, "
              "then come back and run this again.")

        return

    print(f"\nTotal queries routed:     {stats['total_queries']}")
    print(f"Total estimated cost:     ${stats['total_cost_usd']:.8f}")
    print(f"Fallbacks triggered:      {stats['total_fallbacks']} "
          f"({stats['fallback_rate'] * 100:.1f}% of all queries)")
 
    print("\nSplit by tier:")
    for tier, count in stats["tier_counts"].items():
        pct = (count / stats["total_queries"]) * 100
        print(f"  {tier:8s}: {count:4d} queries ({pct:.1f}%)")
 
    print("\nAverage latency:")
    if stats["avg_latency_weak"] is not None:
        print(f"  weak (local):  {stats['avg_latency_weak']}s")
    if stats["avg_latency_strong"] is not None:
        print(f"  strong (cloud): {stats['avg_latency_strong']}s")
 
    print("=" * 60)
 
 
if __name__ == "__main__":
    main()
