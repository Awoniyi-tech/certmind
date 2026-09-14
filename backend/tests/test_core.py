"""Fast, dependency-light regression tests for CertMind core safety logic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.evaluation_service import evaluate_response
from services.question_validation import deduplicate_questions


def test_evaluation_passes_valid_response():
    result = evaluate_response(
        "OSPF is a link-state routing protocol.",
        expected="OSPF is a link-state routing protocol.",
        required_phrases=["OSPF"],
        forbidden_phrases=["password"],
    )
    assert result["passed"] is True
    assert result["score"] == 100.0


def test_evaluation_detects_forbidden_phrase():
    result = evaluate_response("I am not sure; password is required.", forbidden_phrases=["password"])
    assert result["passed"] is False


def test_question_import_deduplicates_and_flags_unanswered():
    questions = [
        {"question": "What is OSPF?", "options": ["A. Link state", "B. Distance vector"], "answer_key": "A"},
        {"question": "What is OSPF?", "options": ["A. Link state", "B. Distance vector"], "answer_key": "A"},
        {"question": "What is BGP?", "options": ["A. Path vector", "B. Link state"], "answer_key": None},
    ]
    accepted, rejected = deduplicate_questions(questions)
    assert len(accepted) == 2
    assert rejected == 1
    assert accepted[1]["needs_review"] is True

