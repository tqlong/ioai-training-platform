from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest
from tests.unit.domain.problems.test_revision import revision

from ioai.application.problems.editorial import (
    ApproveRevision,
    RequestChanges,
    StartSuccessorDraft,
    SubmitForReview,
)
from ioai.application.problems.errors import (
    DraftValidationError,
    RevisionConflictError,
)
from ioai.domain.problems.identity import RevisionId
from ioai.domain.problems.revision import ProblemRevision
from ioai.domain.problems.workflow import ActorContext, EditorialStatus
from ioai.domain.vocabulary.availability import Release0AvailabilityPolicy

NOW = datetime(2026, 8, 9, 10, tzinfo=UTC)


class FakeEditorialRepository:
    def __init__(self, current: ProblemRevision) -> None:
        self.current = current
        self.transitions = []

    def transition(self, transition, *, expected_version, transition_id):
        if expected_version != self.current.version:
            raise RevisionConflictError(self.current.revision_id, self.current.version)
        self.transitions.append((transition_id, transition))
        self.current = replace(
            self.current,
            status=transition.target,
            version=self.current.version + 1,
        )
        return self.current

    def create_successor(
        self, source, successor, *, operation_id, request_digest, created_at
    ):
        del operation_id, request_digest, created_at
        assert source == self.current
        self.current = successor
        return successor


class FakeEditorialWork:
    def __init__(self, current: ProblemRevision) -> None:
        self.drafts = self
        self.editorial = FakeEditorialRepository(current)
        self.current = current
        self.commits = 0

    def get(self, revision_id: RevisionId) -> ProblemRevision:
        assert revision_id == self.current.revision_id
        return self.editorial.current

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.commits += 1


def command(command_type, current: ProblemRevision):
    work = FakeEditorialWork(current)
    use_case = command_type(
        unit_of_work_factory=lambda: work,
        policy=Release0AvailabilityPolicy(),
        id_generator=lambda: "transition-01",
        clock=lambda: NOW,
    )
    return work, use_case


def test_submit_for_review_validates_and_records_current_persisted_state() -> None:
    work, submit = command(SubmitForReview, revision())

    result = submit(
        RevisionId("revision-01"),
        expected_version=1,
        note="Ready for editorial review.",
        actor=ActorContext("local-author"),
        operation_id="submit-01",
    )

    assert result.status is EditorialStatus.IN_REVIEW
    assert result.version == 2
    assert work.editorial.transitions[0][1].occurred_at == NOW
    assert work.commits == 1


def test_submit_with_validation_blockers_changes_nothing() -> None:
    invalid = revision(slug=None)
    work, submit = command(SubmitForReview, invalid)

    with pytest.raises(DraftValidationError) as caught:
        submit(
            invalid.revision_id,
            expected_version=1,
            note="Please review.",
            actor=ActorContext("local-author"),
            operation_id="submit-01",
        )

    assert caught.value.report.publication_eligible is False
    assert work.editorial.transitions == []
    assert work.editorial.current.status is EditorialStatus.DRAFT
    assert work.commits == 0


def test_request_changes_requires_current_in_review_version() -> None:
    current = revision(status=EditorialStatus.IN_REVIEW, version=3)
    work, request_changes = command(RequestChanges, current)

    with pytest.raises(RevisionConflictError):
        request_changes(
            current.revision_id,
            expected_version=2,
            note="Clarify the worked example.",
            actor=ActorContext("local-reviewer"),
            operation_id="changes-01",
        )

    assert work.editorial.transitions == []


def test_approval_revalidates_and_remains_distinct_from_publication() -> None:
    current = revision(status=EditorialStatus.IN_REVIEW, version=2)
    work, approve = command(ApproveRevision, current)

    result = approve(
        current.revision_id,
        expected_version=2,
        note="Approved after checking content and scoring.",
        actor=ActorContext("local-reviewer"),
        operation_id="approve-01",
    )

    assert result.status is EditorialStatus.APPROVED
    assert result.status is not EditorialStatus.PUBLISHED
    assert work.editorial.transitions[0][1].target is EditorialStatus.APPROVED


def test_changes_requested_creates_a_new_draft_without_mutating_reviewed_revision() -> (
    None
):
    reviewed = revision(status=EditorialStatus.CHANGES_REQUESTED, version=4)
    work = FakeEditorialWork(reviewed)
    start = StartSuccessorDraft(
        unit_of_work_factory=lambda: work,
        id_generator=lambda: "revision-02",
        clock=lambda: NOW,
    )

    successor = start(
        reviewed.revision_id, expected_version=4, operation_id="revise-01"
    )

    assert successor.revision_id == RevisionId("revision-02")
    assert successor.problem_id == reviewed.problem_id
    assert successor.status is EditorialStatus.DRAFT
    assert successor.version == 1
    assert successor.content == reviewed.content
    assert reviewed.status is EditorialStatus.CHANGES_REQUESTED


def test_published_revision_creates_private_successor_with_stable_slug() -> None:
    published = revision(status=EditorialStatus.PUBLISHED, version=5)
    work = FakeEditorialWork(published)
    start = StartSuccessorDraft(
        unit_of_work_factory=lambda: work,
        id_generator=lambda: "revision-02",
        clock=lambda: NOW,
    )

    successor = start(
        published.revision_id, expected_version=5, operation_id="revise-published"
    )

    assert successor.status is EditorialStatus.DRAFT
    assert successor.slug == published.slug
    assert published.status is EditorialStatus.PUBLISHED
