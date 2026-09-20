import os
import time
import ollama
from groq import Groq
from dotenv import load_dotenv


load_dotenv()

def call_ollama(model_name: str, query: str) -> dict:
    start = time.time()
    response = ollama.chat(
        model = model_name,
        messages = [{"role": "user", "content": query}],
    )
    elapsed = time.time() - start

    return {
        "answer": response["message"]["content"],
        "latency_seconds": round(elapsed, 2),
        "input_tokens": response.get("prompt_eval_count", 0),
        "output_tokens": response.get("eval_count", 0),
    }


def call_groq(model_name: str, query: str) -> dict:

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    start = time.time()
    response = client.chat.completions.create(
        model = model_name,
        messages = [{"role": "user", "content": query}],
    )
    elapsed = time.time() - start
    
    usage = response.usage

    return {
        "answer": response.choices[0].message.content,
        "latency_seconds": round(elapsed, 2),
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
    }

def call_model(provider: str, model_name: str, query: str) -> dict:
    
    if provider == "ollama":
        return call_ollama(model_name, query)
    
    elif provider == "groq":
        return call_groq(model_name, query)

    else:
        raise ValueError(f"Unknown provider: {provider}")
        
