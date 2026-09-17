"""Provider-isolated model execution with basic latency, usage, and cost metrics."""

import os
from typing import Any


MODEL_PRICING = {
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
}


async def run_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> dict[str, Any]:
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not configured.")
    from services.provider_manager import invoke_gemini
    result = await invoke_gemini(prompt, model_name)
    input_tokens = result["input_tokens"]
    output_tokens = result["output_tokens"]
    pricing = MODEL_PRICING.get(model_name, {"input": 0.0, "output": 0.0})
    estimated_cost = round((input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000, 8)
    return {
        "text": result["text"],
        "model": model_name,
        "latency_ms": result["latency_ms"],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost,
    }

