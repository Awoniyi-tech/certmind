"""Optional advanced evaluators for CertMind.

Deterministic checks remain the default. These functions are explicit opt-in
operations for evaluation workflows and are never called during practice.
"""

import json
import re


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9][a-z0-9_./-]{2,}", (value or "").lower()))


def lexical_similarity(response: str, expected: str) -> float:
    left, right = _tokens(response), _tokens(expected)
    if not left or not right:
        return 0.0
    return round(len(left & right) / len(left | right), 4)


def semantic_similarity(response: str, expected: str) -> float:
    from services.rag_service import _get_embed_model
    model = _get_embed_model()
    vectors = model.encode([response, expected], normalize_embeddings=True)
    return round(float(vectors[0] @ vectors[1]), 4)


def parse_judge_response(text: str) -> dict:
    cleaned = (text or "").strip()
    if cleaned.startswith("FENCE"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        cleaned = cleaned.removesuffix("FENCE").strip()
    try:
        result = json.loads(cleaned)
    except Exception:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        result = json.loads(cleaned[start:end + 1]) if start >= 0 and end > start else {}
    if not isinstance(result, dict):
        raise ValueError("Judge response was not an object.")
    score = max(0, min(5, float(result.get("score", 0))))
    return {
        "score": score,
        "passed": score >= 3.5,
        "reason": str(result.get("reason", ""))[:2000],
        "criteria": result.get("criteria", {}),
    }
