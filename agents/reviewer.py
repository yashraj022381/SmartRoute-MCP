import re

from router.router import route_query
from agents.config import MAX_FACTUAL_REVISIONS, MAX_STYLISTIC_REVISIONS


def reviewer_node(state: dict) -> dict:
    topic = state["topic"]
    draft = state["draft"]
    
    prompt = (
        f"Evalute this draft article about '{topic}' for factual accuracy, "
        f"clarity, and completeness:\n\n{draft}\n\n"
        f"Respond in EXACTLY this format:\n"
        f"VERDICT: APPROVED or NEEDS_REVISION\n"
        f"ISSUE_TYPE: FACTUAL or STYLISTIC or NONE\n"
        f"FEEDBACK: <one or two sentences of specific feedback, or 'None' if approved>\n\n"
        f"Use ISSUE_TYPE: FACTUAL only when the draft contains incorrect, "
        f"missing, or unsupported factual claims that would need new "
        f"research to fix. Use ISSUE_TYPE: STYLISTIC when the facts are fine "
        f"but tone, clarity, structure, or wording need work. Use "
        f"ISSUE_TYPE: NONE only if APPROVED."
        f"Also check whether the article is actually about the stated topic - "
        f"if it drifts into unrelated subject matter, treat this as ISSUE_TYPE: "
        f"FACTUAL, since it means the underlying research was wrong, not just "
        f"the writing style."
    )

    result = route_query(prompt, agent = "reviewer", classify_on=topic)
    answer = result["answer"]

    #verdict = "APPROVED"
    verdict_match = re.search(
        r"VERDICT:?\**\s*(APPROVED|NEEDS_REVISION)", answer, re.IGNORECASE
    )
    verdict = verdict_match.group(1).upper() if verdict_match else "APPROVED"

    issue_type_match = re.search(
        r"ISSUE_TYPE:?\**\s*(FACTUAL|STYLISTIC|NONE)", answer, re.IGNORECASE
    )

    issue_type = issue_type_match.group(1).upper() if issue_type_match else "STYLISTIC"


    feedback_match = re.search(
        r"FEEDBACK:?\**\s*(.+)", answer, re.IGNORECASE | re.DOTALL
    )
    raw_feedback = feedback_match.group(1).strip() if feedback_match else ""
    feedback = "" if raw_feedback.lower().startswith("none") else raw_feedback

    
    needs_revision = verdict == "NEEDS_REVISION"


    factual_hit = needs_revision and issue_type == "FACTUAL"
    stylistic_hit = needs_revision and issue_type == "STYLISTIC"


    #existing_factual = state.get("factual_revision_count", 0)
    #existing_stylistic = state.get("stylistic_revision_count", 0)

    new_factual_count = state.get("factual_revision_count", 0) + (1 if factual_hit else 0)
    new_stylistic_count = state.get("stylistic_revision_count", 0) + (1 if stylistic_hit else 0)

    

    if factual_hit and new_factual_count <= MAX_FACTUAL_REVISIONS:
        next_route = "revise_research"
    elif stylistic_hit and new_stylistic_count <= MAX_STYLISTIC_REVISIONS:
        next_route = "revise_write"
    else:
        next_route = "finalize"

   

    log_entry = {
        "agent": "reviewer",
        "tier_used": result["tier_used"],
        "model_used": result["model_used"],
        "complexity_score": result["complexity_score"],
        "estimated_cost_usd": result["estimated_cost_usd"],
        "fallback_triggered": result["fallback_triggered"],
        "verdict": verdict,
        "issue_type": issue_type if needs_revision else "NONE",
        #"redo_granted": redo_target is not None,
        "next_route": next_route,
        "raw_response": answer,
    }

    #factual_hit = needs_revision and issue_type == "FACTUAL"
    #stylistic_hit = needs_revision and issue_type == "STYLISTIC"


    return {
        "verdict": verdict,
        "issue_type": issue_type if needs_revision else "",
        #"feedback": feedback if verdict == "NEEDS_REVISION" else "",
        "feedback": feedback if needs_revision else "",
        #"redo_target": redo_target,
        #"revision_count": state["revision_count"] + (1 if verdict == "NEEDS_REVISION" else 0),
        #"revision_count": state["revision_count"] + (1 if redo_target else 0),
        #"factual_revision_count": state.get("factual_revision_count", 0) + (1 if factual_hit else 0),
        "revision_count": state.get("revision_count", 0) + (1 if needs_revision else 0),
        #"factual_revision_count": existing_factual + (1 if factual_granted else 0),
        #"stylistic_revision_count": state.get("stylistic_revision_count", 0) + (1 if stylistic_hit else 0),
        #"stylistic_revision_count": existing_stylistic + (1 if stylistic_granted else 0),
        "factual_revision_count": new_factual_count,
        "stylistic_revision_count": new_stylistic_count,
        "next_route": next_route,
        "routing_log": state["routing_log"] + [log_entry],
    } 
