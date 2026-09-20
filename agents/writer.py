from router.router import route_query
from agents.topic_utils import is_pure_arithmetic


def writer_node(state: dict) -> dict:
    topic = state["topic"]
    research_notes = state["research_notes"]
    feedback = state.get("feedback", "")
    is_revision = bool(feedback)

    is_arithmetic = is_pure_arithmetic(topic) and not is_revision



    #if is_pure_arithmetic (topic) and not is_revision:
    if is_arithmetic:
        prompt = (
            f"Answer this directly: '{topic}'\n\n"
            f"Give ONLY the direct answer in one short sentence (e.g. "
            f"the calculated result). Do not write an article, do not "
            f"add background, examples, or extra explanation unless the "
            f"question explicitly asks for them."
        )

    elif is_revision:
        prompt = (
            f"You previously wrote a draft article about '{topic}' using these "
            f"research notes:\n{research_notes}\n\n"
            f"A reviewer gave this feedback:\n{feedback}\n\n"
            f"Write an IMPROVED short article (3-4 paragraphs) that fixes the "
            f"issues raised in the feedback."
        )
    else:
        prompt = (
            f"Using these research notes:\n{research_notes}\n\n"
            f"Write a short article (3-4 paragraphs) about '{topic}' for a "
            f"general audience."
        )
        
    min_len = 1 if is_arithmetic else 10
    result = route_query(prompt, agent = "writer", classify_on=topic, min_useful_length=min_len)

    log_entry = {
        "agent": "writer",
        "tier_used": result["tier_used"],
        "model_used": result["model_used"],
        "complexity_score": result["complexity_score"],
        "estimated_cost_usd": result["estimated_cost_usd"],
        "fallback_triggered": result["fallback_triggered"],
        "was_revision": is_revision,
    }

    return {
        "draft": result["answer"],
        "routing_log": state["routing_log"] + [log_entry],
    }
