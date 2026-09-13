"""Provider-isolated model execution with basic latency, usage, and cost metrics."""

import os
import time
from typing import Any


MODEL_PRICING = {
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
}


async def run_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> dict[str, Any]:
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not configured.")
    from langchain_google_genai import ChatGoogleGenerativeAI

    started = time.perf_counter()
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.1,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    message = await llm.ainvoke(prompt)
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    usage = getattr(message, "usage_metadata", None) or {}
    input_tokens = usage.get("input_tokens") or usage.get("prompt_token_count") or 0
    output_tokens = usage.get("output_tokens") or usage.get("candidates_token_count") or 0
    pricing = MODEL_PRICING.get(model_name, {"input": 0.0, "output": 0.0})
    estimated_cost = round((input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000, 8)
    return {
        "text": message.content if isinstance(message.content, str) else str(message.content),
        "model": model_name,
        "latency_ms": latency_ms,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost,
    }

