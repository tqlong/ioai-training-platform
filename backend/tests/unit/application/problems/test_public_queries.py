from __future__ import annotations

from datetime import UTC, datetime

from ioai.application.problems.public_queries import project_public_snapshot
from ioai.application.problems.publication import PublishedSnapshot
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug


def test_public_projection_omits_internal_and_hidden_assessment_fields() -> None:
    snapshot = PublishedSnapshot(
        "snapshot-1",
        ProblemId("problem-1"),
        RevisionId("revision-secret"),
        StableSlug("metrics-basics"),
        {
            "content": {
                "title": {"en": "Metrics", "vi": "Độ đo", "vi_state": "COMPLETE"},
                "summary": {"en": "Calculate metrics", "vi": "Tính độ đo"},
            },
            "metadata": {"stage": {"code": "AI_1_FOUNDATIONS"}},
            "response": {
                "type": "QUIZ_SINGLE",
                "choices": [{"id": "a", "content": {"en": "A", "vi": "Á"}}],
                "correct_choice_id": "a",
                "hidden_tests": [{"id": "secret", "expected": "answer"}],
                "public_tests": [{"id": "shown", "expected": "1"}],
            },
            "scoring": {"components": [{"method": "EXACT_MATCH"}]},
            "editorial_status": "PUBLISHED",
        },
        datetime(2026, 8, 9, tzinfo=UTC),
    )

    result = project_public_snapshot(snapshot)

    assert result.slug == "metrics-basics"
    assert result.content["title"] == {"en": "Metrics", "vi": "Độ đo"}
    assert "correct_choice_id" not in result.response_schema
    assert "hidden_tests" not in result.response_schema
    assert result.response_schema["public_tests"] == [{"id": "shown", "expected": "1"}]
    serialized = repr(result)
    assert "revision-secret" not in serialized
    assert "editorial_status" not in serialized
    assert "scoring" not in serialized
