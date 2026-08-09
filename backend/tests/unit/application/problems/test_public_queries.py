from __future__ import annotations

from datetime import UTC, datetime

import pytest

from ioai.application.problems.public_queries import (
    ListPublishedProblems,
    PublicProblemPage,
    PublicProblemQuery,
    PublicProblemSort,
    project_public_snapshot,
)
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


class CapturingReader:
    def __init__(self, page: PublicProblemPage) -> None:
        self.page = page
        self.query: PublicProblemQuery | None = None

    def list_current(self, query: PublicProblemQuery) -> PublicProblemPage:
        self.query = query
        return self.page

    def get_current_by_slug(self, slug: str):
        del slug
        return None


def test_list_use_case_passes_canonical_filters_and_preserves_page_metadata() -> None:
    snapshot = PublishedSnapshot(
        "snapshot-1",
        ProblemId("problem-1"),
        RevisionId("revision-1"),
        StableSlug("metrics-basics"),
        {"content": {"title": {"en": "Metrics", "vi": "Độ đo"}}},
        datetime(2026, 8, 9, tzinfo=UTC),
    )
    reader = CapturingReader(PublicProblemPage((snapshot,), total=7))
    query = PublicProblemQuery(
        stage="AI_1_FOUNDATIONS",
        topic="ML_EVALUATION",
        include_subtopics=True,
        search="độ đo",
        sort=PublicProblemSort.TITLE,
        page=2,
        page_size=1,
    )

    result = ListPublishedProblems(reader)(query)

    assert reader.query == query
    assert result.total == 7
    assert result.page == 2
    assert result.page_size == 1
    assert result.items[0].slug == "metrics-basics"


def test_public_problem_query_rejects_unbounded_or_invalid_values() -> None:
    with pytest.raises(ValueError, match="page size"):
        PublicProblemQuery(page_size=101)
    with pytest.raises(ValueError, match="expected minutes"):
        PublicProblemQuery(expected_minutes_min=30, expected_minutes_max=10)
    with pytest.raises(ValueError, match="search"):
        PublicProblemQuery(search="x" * 129)
