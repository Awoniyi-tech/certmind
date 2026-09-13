"""Deterministic evaluation primitives for prompt and RAG experiments."""

import json
import re
from typing import Any


def evaluate_response(
    response: str,
    expected: str | None = None,
    required_phrases: list[str] | None = None,
    forbidden_phrases: list[str] | None = None,
    max_length: int | None = None,
    require_json: bool = False,
) -> dict[str, Any]:
    """Return transparent checks and a normalized 0-100 deterministic score."""
    text = response or ""
    checks: list[dict[str, Any]] = []

    checks.append({"name": "non_empty", "passed": bool(text.strip()), "detail": "Response is not empty."})
    for phrase in required_phrases or []:
        checks.append({"name": f"required:{phrase}", "passed": phrase.lower() in text.lower(), "detail": f"Contains required phrase: {phrase}"})
    for phrase in forbidden_phrases or []:
        checks.append({"name": f"forbidden:{phrase}", "passed": phrase.lower() not in text.lower(), "detail": f"Does not contain forbidden phrase: {phrase}"})
    if max_length is not None:
        checks.append({"name": "max_length", "passed": len(text) <= max_length, "detail": f"Length is {len(text)}; maximum is {max_length}."})
    if require_json:
        try:
            json.loads(text)
            json_ok = True
        except (TypeError, json.JSONDecodeError):
            json_ok = False
        checks.append({"name": "valid_json", "passed": json_ok, "detail": "Response is valid JSON."})
    if expected:
        similarity = _token_overlap(text, expected)
        checks.append({"name": "reference_overlap", "passed": similarity >= 0.5, "score": round(similarity, 3), "detail": "Token overlap with the reference answer."})

    passed = sum(1 for check in checks if check["passed"])
    score = round((passed / len(checks)) * 100, 1) if checks else 0
    return {"score": score, "passed": score >= 70, "checks": checks}


def _token_overlap(left: str, right: str) -> float:
    tokenize = lambda value: set(re.findall(r"[a-z0-9]{3,}", value.lower()))
    expected_tokens = tokenize(right)
    if not expected_tokens:
        return 0.0
    return len(tokenize(left) & expected_tokens) / len(expected_tokens)

