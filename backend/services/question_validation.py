"""Validation and deduplication helpers for imported exam questions."""

import hashlib
import json
import re
from typing import Iterable


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def question_fingerprint(question: dict) -> str:
    """Create a stable fingerprint used to detect duplicate questions."""
    payload = {
        "question": normalize_text(question.get("question", "")),
        "options": [normalize_text(option) for option in question.get("options", [])],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def validate_question(question: dict) -> list[str]:
    errors: list[str] = []
    text = (question.get("question") or "").strip()
    options = question.get("options") or []
    answer_key = question.get("answer_key")
    if len(text) < 10:
        errors.append("question text is too short")
    if len(text) > 10000:
        errors.append("question text is too long")
    if len(options) < 2:
        errors.append("at least two options are required")
    if len({normalize_text(option) for option in options}) != len(options):
        errors.append("options contain duplicates")
    valid_keys = {str(index) for index in range(len(options))}
    valid_keys.update(chr(ord("A") + index) for index in range(min(len(options), 26)))
    keys = answer_key if isinstance(answer_key, list) else [answer_key]
    if answer_key is not None and any(str(key).upper().strip() not in valid_keys for key in keys):
        errors.append("answer key does not reference an available option")
    return errors


def deduplicate_questions(questions: Iterable[dict]) -> tuple[list[dict], int]:
    """Return valid unique questions and the number rejected as duplicates/invalid."""
    accepted: list[dict] = []
    seen: set[str] = set()
    rejected = 0
    for question in questions:
        errors = validate_question(question)
        fingerprint = question_fingerprint(question)
        if errors or fingerprint in seen:
            rejected += 1
            continue
        question["fingerprint"] = fingerprint
        question["needs_review"] = bool(question.get("needs_review") or question.get("answer_key") is None)
        seen.add(fingerprint)
        accepted.append(question)
    return accepted, rejected
