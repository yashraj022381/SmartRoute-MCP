from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    topic: str              # what the user wants a report on
    research_notes: str     # filled in by the Researcher
    draft: str               # filled in (and re-filled, if revised) by the Writer
    feedback: str            # filled in by the Reviewer
    verdict: str              # "APPROVED" or "NEEDS_REVISION"
    issue_type: str            # "FACTUAL" or "STYLISTIC" (only meaningful when NEEDS_REVISION)
    #redo_target: Optional[str]  # "researcher", "writer", or None - set by the Reviewer,
                                  # the single source of truth for routing 
    revision_count: int       # how many times we've looped back to the Writer
    factual_revision_count: int    # factual-triggered revisions used (capped independently)
    stylistic_revision_count: int  # stylistic-triggered revisions used (capped independently)
    next_route: str            # decided by reviewer_node itself: "revise_research" / "revise_write" / "finalize"
    final_output: str          # the finished report, once approved
    routing_log: List[dict]    # a running diary of every routing decision made

