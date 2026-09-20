MODELS = {
    "weak": {
        "name": "llama3.2:1b",
        "provider": "ollama",
        "description": "Small local model. Free, fast, good for simple stuff.",
        "input_cost_per_million": 0.0,
        "output_cost_per_million": 0.0,
    },
    "strong": {
        "name": "openai/gpt-oss-120b",
        "provider": "groq",
        "description": "Large cloud model. Costs a little, msuch smarter.",
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
