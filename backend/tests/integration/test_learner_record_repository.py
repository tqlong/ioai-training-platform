from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from ioai.adapters.database.problem_repository import (
    SqlAlchemyAssessmentUnitOfWork,
    SqlAlchemyLearnerRecordRepository,
)
from ioai.application.problems.assessment import AssessSubmission, SubmissionCommand
from ioai.application.problems.feedback import (
    RecordProblemFeedback,
    SubmitFeedbackCommand,
)
from ioai.application.problems.learner_records import (
    FeedbackCategory,
    LearnerAttempt,
    LearnerOutcome,
    ProblemFeedback,
)

from .test_vocabulary_migration import migrated_database

__all__ = ["migrated_database"]


NOW = datetime(2026, 8, 9, tzinfo=UTC)


def seed_published_problem(database, public_payload: str = "{}") -> str:
    with database.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO problem (problem_id, slug, created_at)
                VALUES ('learner-problem', 'learner-problem', now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO problem_revision
                    (revision_id, problem_id, revision_number, lock_version,
                     editorial_status, content, created_at, updated_at)
                VALUES ('learner-revision', 'learner-problem', 1, 1,
                        'PUBLISHED', '{}', now(), now())
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO published_snapshot
                    (snapshot_id, problem_id, revision_id, slug, public_payload,
                     published_at)
                VALUES ('learner-snapshot', 'learner-problem', 'learner-revision',
                        'learner-problem', CAST(:payload AS jsonb), now())
                """
            ),
            {"payload": public_payload},
        )
        connection.execute(
            text(
                """
                UPDATE problem SET current_published_snapshot_id = 'learner-snapshot'
                WHERE problem_id = 'learner-problem'
                """
            )
        )
    return "learner-snapshot"


def test_assessment_unit_of_work_resolves_current_snapshot_and_commits_once(
    migrated_database,
) -> None:
    seed_published_problem(
        migrated_database,
        '{"response":{"type":"QUIZ_SINGLE","correct_choice_id":"a"},"scoring":{"response_type":"QUIZ_SINGLE","components":[{"method":"EXACT_MATCH","weight":"1.0","configuration":null}]},"metadata":{"resources":{"compute_tier":["COMPUTE_TIER","NONE"]}}}',
    )
    use_case = AssessSubmission(
        lambda: SqlAlchemyAssessmentUnitOfWork(sessionmaker(migrated_database)),
        lambda: "attempt-assessed",
        lambda: NOW,
    )
    command = SubmissionCommand(
        "learner-problem",
        "submission-assessed",
        {"type": "QUIZ_SINGLE", "choice_id": "a"},
    )

    assert use_case(command).result["score"] == "1.0"
    assert use_case(command).attempt_id == "attempt-assessed"


def test_feedback_use_case_commits_and_replays_one_public_snapshot_record(
    migrated_database,
) -> None:
    seed_published_problem(migrated_database)

    class Allow:
        def allow(self, token: str) -> bool:
            return bool(token)

    use_case = RecordProblemFeedback(
        lambda: SqlAlchemyAssessmentUnitOfWork(sessionmaker(migrated_database)),
        lambda: "feedback-use-case",
        lambda: NOW,
        Allow(),
    )
    command = SubmitFeedbackCommand(
        "learner-problem",
        "feedback-command-key",
        FeedbackCategory.CONTENT_ISSUE,
        "The prompt is ambiguous.",
        "anonymous-token",
    )
    assert use_case(command).feedback_id == "feedback-use-case"
    assert use_case(command).feedback_id == "feedback-use-case"


def test_records_attempt_and_replays_same_submission(migrated_database) -> None:
    snapshot_id = seed_published_problem(migrated_database)
    with Session(migrated_database) as session:
        repository = SqlAlchemyLearnerRecordRepository(session)
        attempt = LearnerAttempt(
            attempt_id="attempt-1",
            snapshot_id=snapshot_id,
            submission_key="submission-1",
            request_digest="a" * 64,
            outcome=LearnerOutcome.ACCEPTED_RESULT,
            result={"score": "1.0"},
            submitted_at=NOW,
        )
        repository.add_attempt(attempt)
        session.commit()

        assert repository.replay_attempt(snapshot_id, "submission-1") == attempt


def test_attempt_cannot_reference_a_revision_or_duplicate_intent(
    migrated_database,
) -> None:
    snapshot_id = seed_published_problem(migrated_database)
    with Session(migrated_database) as session:
        repository = SqlAlchemyLearnerRecordRepository(session)
        repository.add_attempt(
            LearnerAttempt(
                attempt_id="attempt-1",
                snapshot_id=snapshot_id,
                submission_key="submission-1",
                request_digest="a" * 64,
                outcome=LearnerOutcome.ACCEPTED_RESULT,
                result={},
                submitted_at=NOW,
            )
        )
        session.commit()
        repository.add_attempt(
            LearnerAttempt(
                attempt_id="attempt-2",
                snapshot_id=snapshot_id,
                submission_key="submission-1",
                request_digest="b" * 64,
                outcome=LearnerOutcome.ACCEPTED_RESULT,
                result={},
                submitted_at=NOW,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_records_feedback_and_rolls_back_failed_transaction(migrated_database) -> None:
    snapshot_id = seed_published_problem(migrated_database)
    feedback = ProblemFeedback(
        feedback_id="feedback-1",
        snapshot_id=snapshot_id,
        feedback_key="feedback-key-1",
        request_digest="c" * 64,
        category=FeedbackCategory.CONTENT_ISSUE,
        message="The example is ambiguous.",
        submitted_at=NOW,
    )
    with Session(migrated_database) as session:
        repository = SqlAlchemyLearnerRecordRepository(session)
        repository.add_feedback(feedback)
        session.rollback()

    with Session(migrated_database) as session:
        repository = SqlAlchemyLearnerRecordRepository(session)
        assert repository.replay_feedback(snapshot_id, "feedback-key-1") is None
