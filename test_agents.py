from agents.graph import run_agent_team

TOPIC = "Why the ocean is salty"


def main():
    print("-" * 70)
    print(f"SmartRoute-MCP - Agent Team Demo")
    print(f"Topic: {TOPIC}")
    print("=" * 70)

    final_state = run_agent_team(TOPIC)

    print("\n--- RESEARCH NOTES ---")
    print(final_state["research_notes"])

    print("\n--- FINAL DRAFT ---")
    print(final_state["draft"])

    if final_state["revision_count"] > 0:
        print("\n--- LAST REVIEWER FEEDBACK ---")
        print(final_state["feedback"] or "(approved on final pass, no feedback stored)")

    print(f"\n--- FINAL ARTICLE ---")
    print(final_state["final_output"])

    print("\n--- ROUTING DIARY (what each agent did) ---")
    total_cost = 0.0
    for i, entry in enumerate(final_state["routing_log"], 1):
        fallback_note = " [FALLBACK TRIGGERED]" if entry.get("fallback_triggered") else ""

        search_note = ""
        if entry["agent"] == "researcher":
            if entry.get("used_cache"):
                search_note = f" [cache hit: {entry.get('cache_match')!r} dist={entry.get('cache_distance')}]"
            elif entry.get("used_web_search"):
                search_note = " [web search: ON]"
            else:
                search_note = f" [web search: FAILED - {entry.get('search_error')}]"

        issue_note = f" issue={entry['issue_type']}" if entry.get("issue_type") else ""
                
        print(f"{i}. [{entry['agent'].upper()}] "
              f"used {entry['tier_used']} ({entry['model_used']}) "
              f"| score={entry['complexity_score']} "
              f"| cost=${entry['estimated_cost_usd']:.8f}"
              f"{fallback_note}{search_note}{issue_note}")
        total_cost += entry["estimated_cost_usd"]

    print(f"\nRevisions needed: {final_state['revision_count']}")
    print(f"  factual revisions used:   {final_state.get('factual_revision_count', 0)}")
    print(f"  stylistic revisions used: {final_state.get('stylistic_revision_count', 0)}")
    print(f"Total cost for this whole article: ${total_cost:.8f}")
    print("=" * 70)

if __name__ == "__main__":
    main()
