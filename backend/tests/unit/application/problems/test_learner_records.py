from datetime import UTC, datetime

import pytest

from ioai.application.problems.learner_records import (
    FeedbackCategory,
    LearnerAttempt,
    LearnerOutcome,
    ProblemFeedback,
)

NOW = datetime(2026, 8, 9, tzinfo=UTC)


def test_learner_attempt_requires_bounded_snapshot_owned_data() -> None:
    attempt = LearnerAttempt(
        attempt_id="attempt-1",
        snapshot_id="snapshot-1",
        submission_key="submission-1",
        request_digest="a" * 64,
        outcome=LearnerOutcome.ACCEPTED_RESULT,
        result={"score": "1.0"},
        submitted_at=NOW,
    )

    assert attempt.snapshot_id == "snapshot-1"
    with pytest.raises(ValueError, match="submission key"):
        LearnerAttempt(
            attempt_id="attempt-2",
            snapshot_id="snapshot-1",
            submission_key="x" * 201,
            request_digest="b" * 64,
            outcome=LearnerOutcome.PENDING_ASSESSMENT,
            result={},
            submitted_at=NOW,
        )
    with pytest.raises(ValueError, match="16384 bytes"):
        LearnerAttempt(
            attempt_id="attempt-3",
            snapshot_id="snapshot-1",
            submission_key="submission-3",
            request_digest="c" * 64,
            outcome=LearnerOutcome.ACCEPTED_RESULT,
            result={"feedback": "x" * 16_384},
            submitted_at=NOW,
        )


def test_problem_feedback_requires_category_and_bounded_message() -> None:
    feedback = ProblemFeedback(
        feedback_id="feedback-1",
        snapshot_id="snapshot-1",
        feedback_key="feedback-key-1",
        request_digest="c" * 64,
        category=FeedbackCategory.CONTENT_ISSUE,
        message="The example is ambiguous.",
        submitted_at=NOW,
    )

    assert feedback.category is FeedbackCategory.CONTENT_ISSUE
    with pytest.raises(ValueError, match="message"):
        ProblemFeedback(
            feedback_id="feedback-2",
            snapshot_id="snapshot-1",
            feedback_key="feedback-key-2",
            request_digest="d" * 64,
            category=FeedbackCategory.OTHER,
            message=" ",
            submitted_at=NOW,
        )
