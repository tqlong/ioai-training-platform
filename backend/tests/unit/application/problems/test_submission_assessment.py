from datetime import UTC, datetime

import pytest

from ioai.application.problems.assessment import AssessSubmission, SubmissionCommand
from ioai.application.problems.errors import IdempotencyConflictError
from ioai.application.problems.learner_records import LearnerOutcome
from ioai.application.problems.publication import PublishedSnapshot
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug

NOW = datetime(2026, 8, 9, tzinfo=UTC)


def snapshot(
    response: dict, scoring: list[dict], compute: str = "NONE"
) -> PublishedSnapshot:
    return PublishedSnapshot(
        "snapshot-1",
        ProblemId("problem-1"),
        RevisionId("revision-private"),
        StableSlug("metrics"),
        {
            "response": response,
            "scoring": {"response_type": response["type"], "components": scoring},
            "metadata": {"resources": {"compute_tier": ["COMPUTE_TIER", compute]}},
        },
        NOW,
    )


class FakeReader:
    def __init__(self, value):
        self.value = value

    def get_current_by_slug(self, slug):
        return self.value if slug == "metrics" else None


class FakeRecords:
    def __init__(self):
        self.attempts = []
        self.feedback = []

    def replay_attempt(self, snapshot_id, submission_key):
        return next(
            (
                item
                for item in self.attempts
                if item.snapshot_id == snapshot_id
                and item.submission_key == submission_key
            ),
            None,
        )

    def add_attempt(self, attempt):
        self.attempts.append(attempt)

    def replay_feedback(self, snapshot_id, feedback_key):
        return next(
            (
                item
                for item in self.feedback
                if item.snapshot_id == snapshot_id and item.feedback_key == feedback_key
            ),
            None,
        )

    def add_feedback(self, item):
        self.feedback.append(item)


class FakeWork:
    def __init__(self, value):
        self.published = FakeReader(value)
        self.records = FakeRecords()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def assessor(value):
    work = FakeWork(value)
    return AssessSubmission(lambda: work, lambda: "attempt-1", lambda: NOW), work


def test_exact_quiz_scores_and_replays_one_snapshot_bound_attempt() -> None:
    use_case, work = assessor(
        snapshot(
            {"type": "QUIZ_SINGLE", "choices": [], "correct_choice_id": "a"},
            [{"method": "EXACT_MATCH", "weight": "1.0", "configuration": None}],
        )
    )
    command = SubmissionCommand(
        "metrics", "key-1", {"type": "QUIZ_SINGLE", "choice_id": "a"}
    )

    first = use_case(command)
    replay = use_case(command)

    assert first is replay
    assert first.outcome is LearnerOutcome.ACCEPTED_RESULT
    assert first.result == {
        "score": "1.0",
        "passed": True,
        "components": [{"method": "EXACT_MATCH", "score": "1.0"}],
    }
    assert len(work.records.attempts) == 1
    assert "revision-private" not in repr(first)


def test_numeric_scoring_is_decimal_safe_and_rejects_changed_idempotent_intent() -> (
    None
):
    use_case, _ = assessor(
        snapshot(
            {
                "type": "NUMERIC_ANSWER",
                "expected": "0.3",
                "absolute_tolerance": "0.0001",
                "unit": None,
            },
            [{"method": "EXACT_MATCH", "weight": "1.0", "configuration": None}],
        )
    )
    assert (
        use_case(
            SubmissionCommand(
                "metrics", "key", {"type": "NUMERIC_ANSWER", "value": "0.1"}
            )
        ).result["score"]
        == "0.0"
    )
    with pytest.raises(IdempotencyConflictError):
        use_case(
            SubmissionCommand(
                "metrics", "key", {"type": "NUMERIC_ANSWER", "value": "0.3"}
            )
        )


def test_human_rubric_stays_pending_without_completion_or_evidence() -> None:
    use_case, _ = assessor(
        snapshot(
            {
                "type": "SHORT_ANSWER",
                "reference_answer": {"en": "because", "vi": "vì"},
                "accepted_keywords": [],
                "rubric_guidance": "Review.",
            },
            [{"method": "RUBRIC_HUMAN", "weight": "1.0", "configuration": None}],
        )
    )
    result = use_case(
        SubmissionCommand(
            "metrics", "key", {"type": "SHORT_ANSWER", "text": "My reasoning"}
        )
    )
    assert result.outcome is LearnerOutcome.PENDING_ASSESSMENT
    assert result.result == {"status": "PENDING_ASSESSMENT"}


def test_code_scoring_uses_injected_evaluator_and_decimal_safe_weighting() -> None:
    class Evaluator:
        def score(self, code, response, method, limits):
            assert code == "def solve(): pass"
            assert method == "PARTIAL_TESTS"
            return __import__("decimal").Decimal("0.5")

    value = snapshot(
        {"type": "CODE_FUNCTION", "hidden_tests": [{"id": "secret"}]},
        [{"method": "PARTIAL_TESTS", "weight": "1.0", "configuration": None}],
        "CPU_LIGHT",
    )
    work = FakeWork(value)
    use_case = AssessSubmission(
        lambda: work, lambda: "attempt-code", lambda: NOW, Evaluator()
    )
    result = use_case(
        SubmissionCommand(
            "metrics",
            "code-key",
            {"type": "CODE_FUNCTION", "code": "def solve(): pass"},
        )
    )
    assert result.result == {
        "score": "0.5",
        "passed": False,
        "components": [{"method": "PARTIAL_TESTS", "score": "0.5"}],
    }
    assert "secret" not in repr(result.result)


@pytest.mark.parametrize("compute", ["GPU_SINGLE", "DISTRIBUTED"])
def test_deferred_compute_tiers_are_rejected(compute: str) -> None:
    use_case, _ = assessor(
        snapshot(
            {"type": "QUIZ_SINGLE", "choices": [], "correct_choice_id": "a"},
            [{"method": "EXACT_MATCH", "weight": "1.0", "configuration": None}],
            compute,
        )
    )
    with pytest.raises(ValueError, match="compute tier"):
        use_case(
            SubmissionCommand(
                "metrics", "key", {"type": "QUIZ_SINGLE", "choice_id": "a"}
            )
        )
