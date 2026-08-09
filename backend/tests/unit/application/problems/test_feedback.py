from datetime import UTC, datetime

import pytest

from ioai.application.problems.errors import (
    IdempotencyConflictError,
    PublishedProblemNotFoundError,
)
from ioai.application.problems.feedback import (
    RecordProblemFeedback,
    SubmitFeedbackCommand,
)
from ioai.application.problems.learner_records import FeedbackCategory
from ioai.application.problems.publication import PublishedSnapshot
from ioai.domain.problems.identity import ProblemId, RevisionId, StableSlug

NOW = datetime(2026, 8, 9, tzinfo=UTC)


def snapshot(response, scoring):
    return PublishedSnapshot(
        "snapshot-1",
        ProblemId("problem-1"),
        RevisionId("revision-private"),
        StableSlug("metrics"),
        {"response": response, "scoring": {"components": scoring}},
        NOW,
    )


class Reader:
    def __init__(self, value):
        self.value = value

    def get_current_by_slug(self, slug):
        return self.value if slug == "metrics" else None


class Records:
    def __init__(self):
        self.feedback = []

    def replay_feedback(self, snapshot_id, key):
        return next(
            (
                item
                for item in self.feedback
                if item.snapshot_id == snapshot_id and item.feedback_key == key
            ),
            None,
        )

    def add_feedback(self, item):
        self.feedback.append(item)


class FakeWork:
    def __init__(self, value):
        self.published = Reader(value)
        self.records = Records()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


class Throttle:
    def __init__(self, allowed=True):
        self.allowed = allowed
        self.tokens = []

    def allow(self, token):
        self.tokens.append(token)
        return self.allowed


def feedback_use_case(allowed=True):
    work = FakeWork(
        snapshot({"type": "QUIZ_SINGLE"}, [{"method": "EXACT_MATCH", "weight": "1.0"}])
    )
    throttle = Throttle(allowed)
    use_case = RecordProblemFeedback(
        lambda: work, lambda: "feedback-1", lambda: NOW, throttle
    )
    return use_case, work, throttle


def test_records_bounded_snapshot_feedback_and_replays_same_intent() -> None:
    use_case, work, throttle = feedback_use_case()
    command = SubmitFeedbackCommand(
        "metrics",
        "key-1",
        FeedbackCategory.TYPO,
        "  There is a typo. ",
        "anonymous-scope",
    )
    first = use_case(command)
    assert use_case(command) is first
    assert first.message == "There is a typo."
    assert first.snapshot_id == "snapshot-1"
    assert len(work.records.feedback) == 1
    assert throttle.tokens == ["anonymous-scope"]


def test_rejects_conflict_limit_and_unpublished_target_without_writes() -> None:
    use_case, work, _ = feedback_use_case()
    use_case(
        SubmitFeedbackCommand(
            "metrics", "key", FeedbackCategory.OTHER, "First", "scope"
        )
    )
    with pytest.raises(IdempotencyConflictError):
        use_case(
            SubmitFeedbackCommand(
                "metrics", "key", FeedbackCategory.OTHER, "Changed", "scope"
            )
        )
    limited, limited_work, _ = feedback_use_case(False)
    with pytest.raises(PermissionError, match="rate"):
        limited(
            SubmitFeedbackCommand(
                "metrics", "other", FeedbackCategory.OTHER, "Message", "scope"
            )
        )
    assert limited_work.records.feedback == []
    missing = FakeWork(None)
    with pytest.raises(PublishedProblemNotFoundError):
        RecordProblemFeedback(lambda: missing, lambda: "id", lambda: NOW, Throttle())(
            SubmitFeedbackCommand(
                "missing", "key", FeedbackCategory.OTHER, "Message", "scope"
            )
        )


@pytest.mark.parametrize("message", ["", "x" * 2001])
def test_rejects_invalid_message_before_storage(message: str) -> None:
    with pytest.raises(ValueError, match="message"):
        SubmitFeedbackCommand(
            "metrics", "key", FeedbackCategory.CONTENT_ISSUE, message, "scope"
        )
