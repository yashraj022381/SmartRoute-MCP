from fastapi import FastAPI, Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from router.router import route_query
from agents.graph import run_agent_team
from db.database import get_summary_stats

app = FastAPI(
    title="SmartRoute-MCP API",
    description="A cost-optimized, MCP-enabled multi-agent AI system.",
)


class RouteRequest(BaseModel):
    query: str


class AgentTeamRequest(BaseModel):
    topic: str


@app.get("/health")
def health():
    """A simple 'are you alive?' check."""
    return {"status": "ok"}


@app.post("/route")
def route(req: RouteRequest):
    """Route a single question to the best model and return the answer."""
    return route_query(req.query)

@app.post("/agent-team")
def agent_team(req: AgentTeamRequest):
     """Run the full Researcher -> Writer -> Reviewer team on a topic."""
     return run_agent_team(req.topic)


@app.get("/stats")
def stats():
    """Return the accumulated performance summary from our database."""
    return get_summary_stats()
    

@app.get("/metrics")
def metrics():
    """
    The 'dashboard' endpoint. Returns all our tracked numbers in the
    standard Prometheus text format - open this directly in a browser
    to see it, or point a real Prometheus server at it to collect
    history and build graphs over time.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
