from datetime import UTC, datetime

import pytest

from ioai.application.problems.learner_records import LearnerAttempt, LearnerOutcome
from ioai.application.problems.manual_assessment import (
    AssessmentConflictError,
    AssessmentRecord,
    AssessmentSelection,
    ListManualAssessments,
    ResolveManualAssessment,
)

NOW = datetime(2026, 8, 11, tzinfo=UTC)


class Records:
    def __init__(self, record):
        self.record = record
        self.decisions = []

    def get_record(self, attempt_id, lock=False):
        del lock
        return self.record if attempt_id == self.record.attempt.attempt_id else None

    def list_records(self, *, status, problem, limit, offset):
        self.list_query = {
            "status": status,
            "problem": problem,
            "limit": limit,
            "offset": offset,
        }
        return (self.record,)

    def add_decision(self, decision):
        self.decisions.append(decision)
        self.record = AssessmentRecord(
            self.record.attempt,
            self.record.slug,
            self.record.title,
            self.record.snapshot_payload,
            decision,
        )

    def complete_attempt(self, attempt_id, result):
        assert attempt_id == self.record.attempt.attempt_id
        self.record = AssessmentRecord(
            LearnerAttempt(
                attempt_id=self.record.attempt.attempt_id,
                snapshot_id=self.record.attempt.snapshot_id,
                submission_key=self.record.attempt.submission_key,
                request_digest=self.record.attempt.request_digest,
                outcome=LearnerOutcome.ACCEPTED_RESULT,
                result=result,
                submitted_at=self.record.attempt.submitted_at,
                receipt_digest=self.record.attempt.receipt_digest,
                response=self.record.attempt.response,
            ),
            self.record.slug,
            self.record.title,
            self.record.snapshot_payload,
            self.record.latest_decision,
        )


class Work:
    def __init__(self, record):
        self.assessments = Records(record)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def pending_record() -> AssessmentRecord:
    attempt = LearnerAttempt(
        "attempt-1",
        "snapshot-1",
        "submission-key",
        "a" * 64,
        LearnerOutcome.PENDING_ASSESSMENT,
        {
            "status": "PENDING_ASSESSMENT",
            "automated_score": "0.4",
            "components": [{"method": "EXACT_MATCH", "score": "1", "weight": "0.4"}],
        },
        NOW,
        "b" * 64,
        {"type": "QUIZ_SINGLE", "choice_id": "a"},
    )
    return AssessmentRecord(
        attempt,
        "precision",
        {"en": "Precision"},
        {
            "scoring": {
                "pass_threshold": "0.7",
                "components": [
                    {"method": "EXACT_MATCH", "weight": "0.4"},
                    {
                        "method": "RUBRIC_HUMAN",
                        "weight": "0.6",
                        "configuration": {
                            "criteria": [
                                {
                                    "id": "reasoning",
                                    "title": {"en": "Reasoning"},
                                    "maximum_points": "2",
                                    "levels": [
                                        {"id": "none", "points": "0"},
                                        {
                                            "id": "complete",
                                            "label": {"en": "Complete"},
                                            "points": "2",
                                        },
                                    ],
                                }
                            ]
                        },
                    },
                ],
            }
        },
    )


def test_resolves_mixed_score_against_snapshot_rubric_and_threshold() -> None:
    work = Work(pending_record())
    resolve = ResolveManualAssessment(lambda: work, lambda: "decision-1", lambda: NOW)

    decision = resolve("attempt-1", (AssessmentSelection(1, "reasoning", "complete"),))

    assert decision.result["score"] == "1.0"
    assert decision.result["passed"] is True
    assert work.assessments.record.attempt.outcome is LearnerOutcome.ACCEPTED_RESULT


def test_lists_bounded_filtered_assessments_through_the_repository_port() -> None:
    work = Work(pending_record())

    records = ListManualAssessments(lambda: work)(
        status="PENDING", problem="precision", limit=25, offset=10
    )

    assert records == (work.assessments.record,)
    assert work.assessments.list_query == {
        "status": "PENDING",
        "problem": "precision",
        "limit": 25,
        "offset": 10,
    }
    with pytest.raises(ValueError, match="pagination"):
        ListManualAssessments(lambda: work)(limit=101)


def test_correction_is_append_only_and_requires_current_identity_and_reason() -> None:
    work = Work(pending_record())
    counter = iter(("decision-1", "decision-2"))
    resolve = ResolveManualAssessment(lambda: work, lambda: next(counter), lambda: NOW)
    first = resolve("attempt-1", (AssessmentSelection(1, "reasoning", "complete"),))

    with pytest.raises(AssessmentConflictError, match="stale"):
        resolve(
            "attempt-1",
            (AssessmentSelection(1, "reasoning", "none"),),
            expected_decision_id="wrong",
            correction_reason="Reviewer correction",
        )
    with pytest.raises(ValueError, match="correction reason"):
        resolve(
            "attempt-1",
            (AssessmentSelection(1, "reasoning", "none"),),
            expected_decision_id=first.decision_id,
        )

    corrected = resolve(
        "attempt-1",
        (AssessmentSelection(1, "reasoning", "none"),),
        expected_decision_id=first.decision_id,
        correction_reason="Reviewer correction",
    )
    assert corrected.version == 2
    assert corrected.result["passed"] is False
    assert len(work.assessments.decisions) == 2


def test_rejects_incomplete_or_unknown_rubric_selections() -> None:
    work = Work(pending_record())
    resolve = ResolveManualAssessment(lambda: work, lambda: "decision", lambda: NOW)

    with pytest.raises(ValueError, match="every rubric criterion"):
        resolve("attempt-1", ())
    with pytest.raises(ValueError, match="selected rubric level"):
        resolve(
            "attempt-1",
            (AssessmentSelection(1, "reasoning", "unknown-level"),),
        )
