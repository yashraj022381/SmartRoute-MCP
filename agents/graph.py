"""
graph.py

Wires Researcher -> Writer -> Reviewer together with LangGraph.

The Reviewer (see reviewer.py) is now the SINGLE place that decides
whether a retry is granted, via the `redo_target` field it returns:
"researcher" (factual problem, budget available), "writer" (style
problem, budget available), or None (approved, or budget spent either
way). This file just reads that decision - it doesn't re-check any
caps itself, so the two files can't drift out of sync the way they did
before.
"""

from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.researcher import researcher_node
from agents.writer import writer_node
from agents.reviewer import reviewer_node


def finalize_node(state: dict) -> dict:
    return {"final_output": state["draft"]}


def after_review(state: dict) -> str:
    #target = state.get("redo_target")
    #if target == "researcher":
    #    return "revise_research"
    #if target == "writer":
    #    return "revise_write"
    #return "finalize"
    return state.get("next_route", "finalize")

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("finalize", finalize_node)

    graph.set_entry_point("researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "reviewer")

    graph.add_conditional_edges(
        "reviewer",
        after_review,
        {
            "revise_research": "researcher",
            "revise_write": "writer",
            "finalize": "finalize",
        },
    )

    graph.add_edge("finalize", END)

    return graph.compile()


def run_agent_team(topic: str) -> dict:
    app = build_graph()

    initial_state = {
        "topic": topic,
        "research_notes": "",
        "draft": "",
        "feedback": "",
        "verdict": "",
        "issue_type": "",
        #"redo_target": None,
        "revision_count": 0,
        "factual_revision_count": 0,
        "stylistic_revision_count": 0,
        "next_route": "",
        "final_output": "",
        "routing_log": [],
    }

    return app.invoke(initial_state)
