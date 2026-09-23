import os

# Controls which model backs the "weak" tier. Defaults to True (real local
# Ollama), which is what your local/Docker setup uses. Set
# USE_LOCAL_WEAK_MODEL=false in the deployed environment (e.g. Render),
# where there's no way to run a persistent local model server, and the
# weak tier automatically becomes Groq's cheapest model instead -
# llama-3.1-8b-instant, at $0.05/$0.08 per million tokens (and often
# free in practice, since it also falls within Groq's free-tier limits).
# Either way, the SAME code path (call_model -> call_ollama/call_groq)
# handles it - nothing else in the app needs to know which mode it's in.
USE_LOCAL_WEAK_MODEL = os.getenv("USE_LOCAL_WEAK_MODEL", "true").lower() == "true"

if USE_LOCAL_WEAK_MODEL:
    WEAK_MODEL = {
        "name": "llama3.2:1b",
        "provider": "ollama",
        "description": "Small local model. Free, fast, good for simple stuff.",
        "input_cost_per_million": 0.0,
        "output_cost_per_million": 0.0,
    }
else:
    WEAK_MODEL = {
        "name": "llama-3.1-8b-instant",
        "provider": "groq",
        "description": (
            "Small, very fast cloud model - stands in for the local Ollama "
            "tier on hosting platforms that can't run a persistent local "
            "model server. Cheapest model on Groq, and usually free in "
            "practice within Groq's own free-tier request limits."
        ),
        "input_cost_per_million": 0.05,
        "output_cost_per_million": 0.08,
    }

MODELS = {
    "weak": WEAK_MODEL,
    "strong": {
        "name": "openai/gpt-oss-120b",
        "provider": "groq",
        "description": "Large cloud model. Costs a little, much smarter.",
        "input_cost_per_million": 0.15,
        "output_cost_per_million": 0.60,
    },
}


def get_model(tier: str) -> dict:
    if tier not in MODELS:
        raise ValueError(f"Unknown model tier '{tier}'. Choose from: {list(MODELS.keys())}")
    return MODELS[tier]


def estimate_cost(tier: str, input_tokens: int, output_tokens: int) -> float:
    model = get_model(tier)
    input_cost = (input_tokens / 1_000_000) * model["input_cost_per_million"]
    output_cost = (output_tokens / 1_000_000) * model["output_cost_per_million"]
    return round(input_cost + output_cost, 8)
