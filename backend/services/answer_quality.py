"""Fast, deterministic answer-quality checks for grounded RAG responses."""

import re


_STOPWORDS = {"the", "and", "or", "a", "an", "is", "are", "to", "of", "in", "for", "on", "with", "this", "that", "what", "how"}


def _terms(value: str) -> set[str]:
    return {
        item for item in re.findall(r"[a-z0-9][a-z0-9_./-]{2,}", (value or "").lower())
        if item not in _STOPWORDS
    }


def evaluate_answer_quality(response: str, expected: str | None = None, evidence: list[str] | None = None, sources: list[str] | None = None) -> dict:
    response_terms = _terms(response)
    evidence_text = " ".join(evidence or [])
    evidence_terms = _terms(evidence_text)
    expected_terms = _terms(expected or "")
    groundedness = len(response_terms & evidence_terms) / max(1, len(response_terms)) if response_terms else 0
    correctness = len(response_terms & expected_terms) / max(1, len(expected_terms)) if expected_terms else None
    relevance = len(response_terms & evidence_terms) / max(1, len(response_terms | evidence_terms)) if evidence_terms else 0
    citation_support = bool(sources) and bool(evidence)
    checks = {
        "non_empty": bool((response or "").strip()),
        "groundedness": round(groundedness, 4),
        "context_relevance": round(relevance, 4),
        "citation_source_support": citation_support,
    }
    if correctness is not None:
        checks["expected_answer_overlap"] = round(correctness, 4)
    score_parts = [groundedness, relevance]
    if correctness is not None:
        score_parts.append(correctness)
    score = round(sum(score_parts) / len(score_parts) * 100, 1)
    return {
        "score": score,
        "passed": bool(response and groundedness >= 0.15 and (correctness is None or correctness >= 0.5)),
        "checks": checks,
        "disclaimer": "Lexical checks are a baseline; semantic and LLM-judge evaluation should be added to the golden set later.",
    }
