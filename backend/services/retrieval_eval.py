"""Retrieval quality metrics for CertMind golden datasets."""

import math


def _is_relevant(doc: dict, expected_sources: list[str], relevant_terms: list[str]) -> bool:
    metadata = doc.get("metadata") or {}
    source = str(metadata.get("source", "")).lower()
    content = str(doc.get("page_content", "")).lower()
    if expected_sources and any(str(item).lower() in source for item in expected_sources):
        return True
    return bool(relevant_terms) and all(str(term).lower() in content for term in relevant_terms)


def evaluate_retrieval(results: list[list[dict]], expected_sources: list[list[str]], relevant_terms: list[list[str]], k: int = 3) -> dict:
    total = len(results)
    if total == 0:
        return {"total_cases": 0, "recall_at_k": 0, "precision_at_k": 0, "mrr": 0, "ndcg_at_k": 0}
    recalls = []
    precisions = []
    reciprocal_ranks = []
    ndcgs = []
    for index, docs in enumerate(results):
        sources = expected_sources[index] if index < len(expected_sources) else []
        terms = relevant_terms[index] if index < len(relevant_terms) else []
        ranked = docs[:k]
        relevance = [_is_relevant(doc, sources, terms) for doc in ranked]
        hit_positions = [position for position, relevant in enumerate(relevance, 1) if relevant]
        recalls.append(1.0 if hit_positions else 0.0)
        precisions.append(sum(relevance) / max(1, k))
        reciprocal_ranks.append(1.0 / hit_positions[0] if hit_positions else 0.0)
        ideal = sum(1.0 / math.log2(position + 1) for position in range(1, min(len(hit_positions), k) + 1))
        actual = sum((1.0 / math.log2(position + 1)) for position, relevant in enumerate(relevance, 1) if relevant)
        ndcgs.append(actual / ideal if ideal else 0.0)
    return {
        "total_cases": total,
        "recall_at_k": round(sum(recalls) / total, 4),
        "precision_at_k": round(sum(precisions) / total, 4),
        "mrr": round(sum(reciprocal_ranks) / total, 4),
        "ndcg_at_k": round(sum(ndcgs) / total, 4),
    }
