"""
manual_test_agents.py

Run this from the project root (`python manual_test_agents.py`) to verify:
  1. The writer.py fix - drafts get produced on revision passes, not None.
  2. Reviewer -> Researcher routing for FACTUAL issues (issue_type == "FACTUAL",
     you should see a later researcher log entry with "was_rerun": True).
  3. Reviewer -> Writer routing for STYLISTIC issues (no re-research triggered).
  4. The pipeline never crashes and always produces a non-empty final_output.

Verdicts are model-dependent, so not every topic will trigger a revision on
every run. Run a few of these, a few times each, and check the printed
summary rather than expecting one guaranteed outcome.
"""

from agents.graph import run_agent_team

# Mix of topics: some simple (likely APPROVED first try), some prone to
# factual nitpicking (obscure/nuanced/changing facts), some prone to
# stylistic nitpicking (clear facts, but easy to write clunkily).
TEST_TOPICS = [
    "The basics of home composting",                     # likely clean pass
    "The current state of commercial nuclear fusion",     # nuanced facts -> possible FACTUAL flag
    "How photosynthesis works",                           # simple facts -> possible STYLISTIC flag
    "The history of the Voyager 1 space probe",           # detail-heavy -> possible FACTUAL flag
]


def summarize(topic: str, result: dict):
    print("=" * 70)
    print(f"TOPIC: {topic}")
    print("-" * 70)

    log = result["routing_log"]
    for entry in log:
        agent = entry["agent"]
        line = f"[{agent:9}] tier={entry.get('tier_used'):6}"

        if agent == "researcher":
            line += f" used_cache={entry.get('used_cache')} was_rerun={entry.get('was_rerun')}"
        if agent == "reviewer":
            line += f" verdict={entry.get('verdict')} issue_type={entry.get('issue_type')}"
        if agent == "writer":
            line += f" was_revision={entry.get('was_revision')}"

        print(line)

    print("-" * 70)
    print(f"Final verdict:     {result['verdict']}")
    print(f"Revision count:    {result['revision_count']}")
    print(f"  factual used:    {result.get('factual_revision_count', 0)}")
    print(f"  stylistic used:  {result.get('stylistic_revision_count', 0)}")
    print(f"Final output len:  {len(result['final_output'])} chars")
    print(f"Final output empty? {'YES <-- BUG' if not result['final_output'].strip() else 'no (good)'}")
    print()


if __name__ == "__main__":
    for topic in TEST_TOPICS:
        try:
            result = run_agent_team(topic)
            summarize(topic, result)
        except Exception as e:
            print("=" * 70)
            print(f"TOPIC: {topic}")
            print(f"CRASHED: {type(e).__name__}: {e}")
            print()
