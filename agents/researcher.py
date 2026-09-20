import re

from router.router import route_query
from mcp_server.client import web_search
from rag.vector_store import add_research, find_similar_research
from agents.topic_utils import is_pure_arithmetic


STOPWORDS = {
    "a","an","the","is","are","was","were","what","who","when","where",
    "why","how","of","in","on","to","and","or","for","with","do","does",
    "did","this","that","it","its","be","can","will","could", "should", "would", "about"
}

#def _keywords(text: str) -> set:
#    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
#    return {w for w in words if w not in STOPWORDS and len(w) > 1}

#def is_topically_relevant(topic: str, notes: str) -> bool:
#    """
#    Cheap, deterministic sanity check - NOT another LLM call, so it costs
#    nothing. Just asks: does this response share even one real keyword
#    with what was actually asked? Catches wild hallucinations like
#    answering 'what is 2+2' with a music history essay, while still
#    tolerating notes that reasonably paraphrase the topic.
#    """
#    topic_kw = _keywords(topic)
#    if not topic_kw:
#        return True  # nothing meaningful to check against, don't block
#    notes_kw = _keywords(notes)
#    return len(topic_kw & notes_kw) >= 1



def _looks_relevant(topic: str, search_results: str) -> bool:
    """
    Generic sanity check, not specific to any one topic type: does the
    search text actually mention meaningful words from the topic? Search
    backends built on scraping (rather than a real search API) can
    return irrelevant or garbage results for all sorts of reasons - odd
    punctuation, rate limiting, blocked requests - and without this check
    the pipeline will happily summarize whatever it's given as if it
    were genuinely about the topic, regardless of what the topic is.
    """
    topic_words = [
        w for w in re.findall(r"[a-zA-Z]+", topic.lower())
        if w not in STOPWORDS and len(w) > 2
    ]
    if not topic_words:
        # No real keywords to check against (e.g. a numeric topic) -
        # nothing meaningful this check can verify either way.
        return True
 
    results_lower = search_results.lower()
    matches = sum(1 for w in topic_words if w in results_lower)
    return matches >= max(1, len(topic_words) // 3)



def researcher_node(state: dict) -> dict:
    topic = state["topic"]
    feedback = state.get("feedback", "")
    is_rerun = bool(feedback)

    if not is_rerun:
        cached = find_similar_research(topic)
        if cached:
            log_entry = {
                "agent": "researcher",
                "tier_used": "cache",
                "model_used": "vector-cache",
                "complexity_score": 0.0,
                "estimated_cost_usd": 0.0,
                "fallback_triggered": False,
                "used_web_search": False,
                "search_error": None,
                "used_cache": True,
                "cache_match": cached["matched_topic"],
                "cache_distance": cached["distance"],
                "was_rerun": False,
            }
            return {
                "research_notes": cached["notes"],
                "routing_log": state["routing_log"] + [log_entry],
            }

        
    skip_search = (not is_rerun) and is_pure_arithmetic(topic)

    if skip_search:
        search_worked = False
        search_error = "Skipped web search - topic looks like a direct calculation, not a lookup."
    else:
        search_query = f"{topic} {feedback}".strip() if is_rerun else topic
        search_results = web_search(search_query, max_results = 5)
        search_worked = not search_results.startswith("Search failed") and \
            search_results != "No search results found."

        if search_worked and not _looks_relevant(topic, search_results):
            # The search "succeeded" in the sense of returning something,
            # but that something doesn't actually mention the topic -
            # treat it the same as a failed search rather than trusting it.
            search_worked = False
            #search_error = None if search_worked else search_results
            search_error = "Search results didn't appear related to the topic - falling back to model knowledge."

        else:
            search_error = None if search_worked else search_results

    if is_rerun:
        base = (
            f"Topic: '{topic}'.\n\n"
            f"A reviewer flagged this factual concern with an earlier draft:\n"
            f"\"{feedback}\"\n\n"
        )
        if search_worked:
            prompt = (
                base +
                f"Stay strictly on the topic - do not introduce unrelated facts, names, "
                f"or trivia. If there isn't much to say, write fewer, shorter points "
                f"rather than padding with unrelated content.\n"
                f"Topic: '{topic}'.\n\n"
                f"Here are real web search results about this topic:\n\n"
                f"{search_results}\n\n"
                f"Based on these search results, write 5-7 short, factual bullet "
                #f"points a writer could use to write an article. Respond with "
                f"points that specifically correct or address the reviewer's "
                f"concern, to replace the earlier research notes. Respond "
                f"with ONLY the bullet points - no preamble."
            )
        else:
            prompt = (
                base +
                f"Stay strictly on the topic - do not introduce unrelated facts, names, "
                f"or trivia. If there isn't much to say, write fewer, shorter points "
                f"rather than padding with unrelated content.\n"
                f"Topic: '{topic}'.\n"
                f"(Web search was unavailable, so use what you already know.)\n"
                f"Based on what you already know, list 5-7 short, factual bullet "
                #f"points a writer could use to write an article on this topic. "
                f"points that address the reviewer's concern. Respond with ONLY the "
                f"bullet points - no preamble, no disclaimers, no asking for clarification."
            )

    elif search_worked:
        prompt = (
            f"Stay strictly on the topic - do not introduce unrelated facts, names, "
            f"or trivia. If there isn't much to say, write fewer, shorter points "
            f"rather than padding with unrelated content.\n"
            f"Topic: '{topic}'.\n\n"
            f"Here are real web search results about this topic:\n\n"
            f"{search_results}\n\n"
            f"Based on these search results, write 5-7 short, factual bullet "
            f"points a writer could use to write an article. Respond with "
            f"ONLY the bullet points - no preamble."
        )
    else:
        prompt = (
            f"Stay strictly on the topic - do not introduce unrelated facts, names, "
            f"or trivia. If there isn't much to say, write fewer, shorter points "
            f"rather than padding with unrelated content.\n"
            f"Topic: '{topic}'.\n"
            f"(Web search was unavailable, so use what you already know.)\n"
            f"Based on what you already know, list 5-7 short, factual bullet "
            f"points a writer could use to write an article on this exact topic. "
            f"Respond with ONLY the bullet points - no preamble, no "
            f"disclaimers, no asking for clarification, and do not drift "
            f"onto a different subject."
        )
 
    
    result = route_query(prompt, agent = "researcher", classify_on=topic)

    #relevance_override = False
    #if result["tier_used"] == "weak" and not is_topically_relevant(topic, result["answer"]):
        # The cheap model's answer doesn't even mention the topic - don't
        # trust it, retry on the strong tier instead.
    #    result = route_query(prompt, agent="researcher", force_tier="strong")
    #    relevance_override = True

    if not is_rerun:
        add_research(topic, result["answer"])

    log_entry = {
        "agent": "researcher",
        "tier_used": result["tier_used"],
        "model_used": result["model_used"],
        "complexity_score": result["complexity_score"],
        "estimated_cost_usd": result["estimated_cost_usd"],
        "fallback_triggered": result["fallback_triggered"],
        "used_web_search": search_worked,
        "search_error": search_error,
        "used_cache": False,
        "cache_match": None,
        "cache_distance": None,
        "was_rerun": is_rerun,
    }

    return {
        "research_notes": result["answer"],
        "routing_log": state["routing_log"] + [log_entry],
    }
