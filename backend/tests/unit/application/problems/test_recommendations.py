from datetime import UTC, datetime

from ioai.application.problems.publication import PublishedSnapshot
from ioai.application.problems.recommendations import (
    LearningEvidenceContext,
    RecommendationContext,
    RecommendNextProblem,
)
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug

NOW = datetime(2026, 8, 9, tzinfo=UTC)


def snapshot(
    slug: str,
    order: int,
    *,
    prerequisites: list[dict[str, object]] | None = None,
) -> PublishedSnapshot:
    return PublishedSnapshot(
        snapshot_id=f"snapshot-{slug}",
        problem_id=ProblemId(f"problem-{slug}"),
        revision_id=RevisionId(f"revision-{slug}"),
        slug=StableSlug(slug),
        public_payload={
            "content": {"title": {"en": slug.title(), "vi": slug.title()}},
            "metadata": {
                "stage": ["PATHWAY_STAGE", "AI_1_FOUNDATIONS"],
                "difficulty": ["DIFFICULTY", "EASY"],
                "primary_competency": ["COMPETENCY", "EVAL_METRICS"],
                "topics": [["TOPIC", "EVAL_CONFUSION_MATRIX"]],
                "task_type": ["TASK_TYPE", "QUIZ_SINGLE"],
                "expected_minutes": 10,
                "editorial_order": order,
                "prerequisites": prerequisites or [],
                "resources": {"compute_tier": ["COMPUTE_TIER", "NONE"]},
            },
        },
        published_at=NOW,
    )


class FakeCandidates:
    def __init__(self, values: tuple[PublishedSnapshot, ...]) -> None:
        self.values = values
        self.stage: str | None = None

    def recommendation_candidates(self, stage: str) -> tuple[PublishedSnapshot, ...]:
        self.stage = stage
        return self.values


def test_recommends_editorial_start_without_claiming_personalization() -> None:
    candidates = FakeCandidates((snapshot("second", 2), snapshot("first", 1)))

    recommendation = RecommendNextProblem(candidates)(
        RecommendationContext(stage="AI_1_FOUNDATIONS")
    )

    assert candidates.stage == "AI_1_FOUNDATIONS"
    assert recommendation is not None
    assert recommendation.slug == "first"
    assert recommendation.label == "Recommended start"
    assert recommendation.reason == "First published problem in this stage."


def test_recommends_unfinished_prerequisite_compatible_next_problem() -> None:
    prerequisite = {
        "relationship": "REQUIRED",
        "target_type": "TOPIC",
        "target_identity": ["TOPIC", "EVAL_CONFUSION_MATRIX"],
        "target_id": None,
        "minimum_evidence": "PRACTICED",
    }
    candidates = FakeCandidates(
        (
            snapshot("current", 1),
            snapshot("blocked", 2, prerequisites=[prerequisite]),
            snapshot("next", 3),
        )
    )
    context = RecommendationContext(
        stage="AI_1_FOUNDATIONS",
        current_slug="current",
        completed_slugs=("current",),
        evidence=(
            LearningEvidenceContext(
                vocabulary_type="TOPIC",
                code="EVAL_CONFUSION_MATRIX",
                level="INTRODUCED",
            ),
        ),
    )

    recommendation = RecommendNextProblem(candidates)(context)

    assert recommendation is not None
    assert recommendation.slug == "next"
    assert recommendation.label == "Recommended next"
    assert "stage and editorial path" in recommendation.reason


def test_returns_safe_empty_outcome_when_no_eligible_alternative_exists() -> None:
    candidates = FakeCandidates((snapshot("done", 1),))

    result = RecommendNextProblem(candidates)(
        RecommendationContext(
            stage="AI_1_FOUNDATIONS",
            current_slug="done",
            completed_slugs=("done",),
        )
    )

    assert result is None
