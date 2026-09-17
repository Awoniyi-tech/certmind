"""Shared Gemini request protection for CertMind AI features."""

import asyncio
import os
import random
import time


_semaphore = asyncio.Semaphore(max(1, int(os.getenv("GEMINI_MAX_CONCURRENCY", "2"))))
_pace_lock = asyncio.Lock()
_last_request_at = 0.0
_consecutive_failures = 0
_circuit_open_until = 0.0


def is_retryable_error(error: Exception) -> bool:
    text = str(error).lower()
    return any(value in text for value in (
        "429", "too many", "resource_exhausted", "503", "service unavailable",
        "temporarily unavailable", "deadline exceeded",
    ))


async def _pace() -> None:
    global _last_request_at
    interval = max(0.0, float(os.getenv("GEMINI_MIN_INTERVAL_SECONDS", "0.8")))
    async with _pace_lock:
        wait_for = interval - (time.monotonic() - _last_request_at)
        if wait_for > 0:
            await asyncio.sleep(wait_for)
        _last_request_at = time.monotonic()


async def invoke_gemini(prompt: str, model: str = "gemini-2.5-flash", max_output_tokens: int | None = None) -> dict:
    """Run one protected Gemini call and return text plus usage metadata."""
    global _consecutive_failures, _circuit_open_until
    if not os.getenv("GOOGLE_API_KEY", "").strip():
        raise RuntimeError("GOOGLE_API_KEY is not configured.")
    if time.monotonic() < _circuit_open_until:
        raise RuntimeError("Gemini provider is cooling down after repeated availability errors.")

    from langchain_google_genai import ChatGoogleGenerativeAI
    attempts = max(1, int(os.getenv("GEMINI_MAX_ATTEMPTS", "2")))
    async with _semaphore:
        for attempt in range(attempts):
            try:
                await _pace()
                started = time.perf_counter()
                llm = ChatGoogleGenerativeAI(
                    model=model,
                    temperature=0.1,
                    max_output_tokens=max_output_tokens,
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                )
                message = await llm.ainvoke(prompt)
                _consecutive_failures = 0
                usage = getattr(message, "usage_metadata", None) or {}
                return {
                    "text": message.content if isinstance(message.content, str) else str(message.content),
                    "model": model,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                    "input_tokens": usage.get("input_tokens") or usage.get("prompt_token_count") or 0,
                    "output_tokens": usage.get("output_tokens") or usage.get("candidates_token_count") or 0,
                }
            except Exception as exc:
                if not is_retryable_error(exc) or attempt == attempts - 1:
                    _consecutive_failures += 1
                    if _consecutive_failures >= 3:
                        _circuit_open_until = time.monotonic() + float(os.getenv("GEMINI_CIRCUIT_COOLDOWN_SECONDS", "20"))
                    raise
                await asyncio.sleep((2 ** attempt) + random.uniform(0.1, 0.5))

    raise RuntimeError("Gemini request failed.")
